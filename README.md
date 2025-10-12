# Weatherapp

## Clone the repository

```bash
git clone https://github.com/DanielDominguezBender/WeatherApp.git
cd WeatherApp
```

## Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\\Scripts\\activate   # For Windows
```
## Install the required dependencies

```python
pip install flet
```
## Get your free API Key

- Go to: https://openweathermap.org/api
- Sign up for a free account
- Visit your dashboard and copy your API Key
- You’ll be asked to paste it the first time you launch the app. It will be saved locally.

## Clone the repository

```bash
git clone https://github.com/DanielDominguezBender/WeatherApp.git
cd WeatherApp
```

## Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\\Scripts\\activate   # For Windows
```
## Install the required dependencies

```python
pip install flet
```
## Get your free API Key

- Go to: https://openweathermap.org/api
- Sign up for a free account
- Visit your dashboard and copy your API Key
- You’ll be asked to paste it the first time you launch the app. It will be saved locally.

## Run the app

Run as a desktop app:

```python
flet run main.py
```

Run as a web app:

```python
flet run main.py --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/getting-started/).

## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).
