## Streamlit & SiS Quick Guide

### Overview
The current folder (`./`) is intended to collect all the Streamlit (and Streamlit in Snowflake) apps into Github for easier managing and iterating. The folders can be uploaded and apps deployed into Snowhouse automatically by running `update_sis.py` script (more details below). Manually created app files can be placed under hidden directorys and they will be ignored by the updater script.

### Create an App
Refer to https://docs.snowflake.com/en/developer-guide/streamlit/create-streamlit-sql#label-streamlit-create-app-files for creating your app locally. For the purposes of easily uploading and deploying apps please place all app files under `./path-to-app/` and updater script will treat the folder as a whole. Library files can be shared via `lib/` directory or any other directory in the same root location.

### Running App Locally
(Not 100% sure if this is necessary but this is what got my stuff working)

Streamlit needs Python virtual environment to be activated in order to run. The workflow looks like:
```
python3 -m venv /tmp/env
source /tmp/env/bin/activate
```
Now we are inside the virtual env, and package installation seems to be a one time setup
```
pip install streamlit snowflake snowflake-snowpark-python "snowflake-connector-python[secure-local-storage]"
```
Run the app! (from current folder)
```
streamlit run example_app/run_app.py
```
If you're seeing issues importing the libary files, append the `lib/` directory to your python path:
```
export PYTHONPATH="${PYTHONPATH}:lib/"
```

### Uploading and Deploying Apps to Snowhouse
`update_sis.py` script has the basic upload & deploy functionalities. First make it executable
```
chmod +x update_sis.py
```

#### Upload
Upload takes in a directory or upload all files, it'll upload all files to your specified stage and keeps the same directory structure. E.g.
```
./update_sis.py upload -d path-to-app
./update_sis.py upload -a
```

#### Deploy
Deploy takes in a directory and you'll need to specify a configuration mode of `auto_config` or `manual_config`:
```
./update_sis.py deploy -d path-to-app {auto_config|manual_config}
```
Auto config mode: `auto_config` will try to read a configuration file named `config.yaml` in the directory of the app by default.
```
./update_sis.py [--overwrite] deploy -d path-to-app auto_config
```
Manual config mode: `manual_config` requires a main-file location for the Streamlit app, it'll upload the app files and create a Streamlit from the location.
```
./update_sis.py deploy -d path-to-app -n full.qualified.app_name --main-file run_app.py --import lib/interactive.py
```

#### Options: Update-if-Not-Exists or Overwrite
For updating an exsiting app, use deploy with `--overwrite` flag. This is because in Snowflake we cannot control the `ROOT_LOCATION` of the app and it's a hassle to directly put files into the interal stage of Streamlit.

#### Manual
For general usage: `./update_sis.py -h`
For deploy: `./update_sis.py deploy -h`, if you need to manually config: `./update_sis.py deploy -d path-to-app manual_config -h`
