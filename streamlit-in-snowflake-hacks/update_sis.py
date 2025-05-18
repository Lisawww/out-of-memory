#!/usr/bin/env python3
# coding: utf-8

import os
import logging
import sys
import argparse
import yaml
import snowflake.connector
from snowflake.connector import DictCursor

PWD = os.path.abspath(os.getcwd())

snowflake_config = {
    # fill in snowflake account config
}

stage_name = '' # fill in stage name for the files uploading


def list_directory(directory, is_dir_or_file):
    # ignore hidden files and system generated files
    return [f for f in os.listdir(directory) if is_dir_or_file(directory + '/' + f) and not f.startswith('.') and not f.startswith('_')]

def upload_file(ctx, directory, file, overwrite):
    f_path = PWD + "/" + directory + "/" + file
    print(f'[DEBUG] Uploading {f_path} to stage @{stage_name}')
    command = f"PUT file://{f_path} @{stage_name}/{directory} AUTO_COMPRESS=FALSE OVERWRITE={overwrite}"
    print(f'[DEBUG] {command}')
    ctx.cursor().execute(command)

def upload_directory_recursively(ctx, directory, overwrite):
    dirs = list_directory(directory, os.path.isdir)
    files = list_directory(directory, os.path.isfile)

    for d in dirs:
        upload_directory_recursively(ctx, directory + "/" + d, overwrite)

    for f in files:
        upload_file(ctx, directory, f, overwrite)


def deploy_app(ctx, name, directory, main_file, warehouse, import_list, overwrite):
    parsed_import_list = ', '.join([f"'@{stage_name}/{f}'" for f in import_list])

    print('[INFO] Uploading imported files')
    for f in import_list:
        f_name_parts = f.split('/')
        upload_file(ctx, '/'.join(f_name_parts[:-1]), f_name_parts[-1], overwrite)

    print(f'[INFO] Uploading directory {directory}')
    upload_directory_recursively(ctx, directory, overwrite)

    allow_replace = 'or replace' if overwrite else ''
    optional_imports = f'imports = ({parsed_import_list})' if import_list else ''

    print(f'[INFO] Deploying Streamlit at {name} with main entry file {main_file}')
    command = f"""create {allow_replace} streamlit {name}
from '@{stage_name}/{directory}/'
main_file = '{main_file}'
query_warehouse = {warehouse}
{optional_imports};"""
    print(f'[DEBUG] {command}')
    ctx.cursor().execute(command)

    add_live_version = f"""alter streamlit {name} add live version from last;"""
    print(f'[DEBUG] {add_live_version}')
    ctx.cursor().execute(add_live_version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"""Upload and deploy Streamlit apps to Snowflake. All files will be uploaded to stage @{stage_name}, \
        under path 'relative_path/to/file'. Library files are also by default loaded from relative paths under the root of the stage.""")
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='if specified, overwrite existing files and Streamlit apps')

    subparsers = parser.add_subparsers(dest='command')

    # create the parser for upload
    parser_upload = subparsers.add_parser('upload', help='upload files to stage, hidden files and system files are ignored.')
    parser_upload.add_argument('-d', '--directory', type=str, help='directory to upload')
    parser_upload.add_argument('-a', '--all', dest='upload_all', action='store_true', help='upload all files')

    # create the parser for deploy
    parser_deploy = subparsers.add_parser('deploy', help='deploy a Streamlit app')
    parser_deploy.add_argument('-d', '--directory', type=str, required=True, help='directory containing the Streamlit app\'s main file')

    deploy_config_subparsers = parser_deploy.add_subparsers(dest='deploy_config_mode', required=True)

    # create the parser for auto-config from a file
    parser_auto_config = deploy_config_subparsers.add_parser('auto_config', help="config app from a configuration yaml file")
    parser_auto_config.add_argument('-f', '--file', dest='config_file', type=str, default='config.yaml', help='name of the configuration file (use relative path inside the app directory)')

    # create the parser for manual configs from command line options
    parser_manual_config = deploy_config_subparsers.add_parser('manual_config', help="config app from manually passed in options")
    parser_manual_config.add_argument('-n', '--name', type=str, required=True, help="""name of the Streamlit app. Please specify full qualified name; \
        if not specified the directory name will be used as app name.""")
    parser_manual_config.add_argument('--main-file', type=str, required=True, help='main entry file of the Streamlit app')
    parser_manual_config.add_argument('--warehouse', type=str, required=True, help='query warehouse for the app')
    parser_manual_config.add_argument('--import', dest='import_list', type=str, nargs="*", default=[], help='list of modules to import, must be .py or .zip files and please use relative paths e.g. lib/interactive.py')

    args = parser.parse_args()

    if not args.command:
        print('[INFO] Command {upload, deploy} not specified, nothing to do')
        parser.print_help()
        exit()

    ctx = snowflake.connector.connect(**snowflake_config)
    dirs = list_directory('.', os.path.isdir)

    if args.command == 'upload':
        if args.upload_all:
            for d in dirs:
                print(f'[INFO] Uploading directory {d}')
                upload_directory_recursively(ctx, d, args.overwrite)
        else:
            directory = args.directory
            if not directory or directory not in dirs:
                raise ValueError(f"Specified directory '{directory}' does not exist or is hidden.")

            print(f'[INFO] Uploading directory {directory}')
            upload_directory_recursively(ctx, directory, args.overwrite)

    elif args.command == 'deploy':
        directory = args.directory

        if args.deploy_config_mode == 'auto_config':
            with open(directory + '/' + args.config_file, 'r') as f:
                configs = yaml.safe_load(f)
            deploy_app(ctx, configs['name'], directory, configs['main_file'], configs['warehouse'], configs['imports'], args.overwrite)
        elif args.deploy_config_mode == 'manual_config':
            name = args.name
            deploy_app(ctx, name, directory, args.main_file, args.warehouse, args.import_list, args.overwrite)
