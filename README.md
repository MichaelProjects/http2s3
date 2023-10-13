## Http2S3
Simple python application to make it easy to use s3 with client-side encryption to store backups or other kind of sensitive information.

## Usage
> [!WARNING]  
>This service was developed to work with the s3 production offered by linode, no guarantee that it will work worth with other providers eg. aws, gcp or digital oceans equivalent products, if you'd like support youre welcome to create a update and create a pull request.

1. Upload your file to specific location

```bash
# example how to use this service with curl (the multi-part header is needed)
curl -X POST -F "file=@test_file.zip" localhost:8777/api/v1/{your_directory_in_bucket}/{filename}.zip
```
2. Download the file you need via the Web GUI of your provider
3. Use the decrypt_file.py to make it readable again
```bash
poetry run python3 decrypt_file.py -f /Users/michael/Downloads/backup01.zip
```
4. If you run the docker version you need to download the scirpt and install some requirements that are needed:
```bash
curl -o decrypt_file.py https://raw.githubusercontent.com/MichaelProjects/http2s3/master/decrypt_file.py
pip install cryptography==41.0.4
export encryption_key=your_encryption_key
``` 

## Install
> **Note**
> If you want to use the client side encryption run the utils.py to generate a fernet encryption key

There are two ways to install, probably the easyist way to run the service is via docker, just fill the environment variables and run the container as described below:

### Docker
1. Pull the image:
```bash
docker pull michaelprojects/http2s3:1.0.0
```
2. Start the container with your secrets:
```bash
docker run -v /absolut/path/to/conf.toml:/conf.toml michaelprojects/http2s3:1.0.0
```
2.1 Run the configure the application via docker environment variables:
```bash
docker run -e debug=false -e encryption_on=true -e port=8000 -e host=0.0.0.0 -e api_key=.. -e secret_key=.. -e cluster_url=.. -e encryption_key=.. -p 0.0.0.0:8000:8000 michaelprojects/http2s3:1.0.0
```

### Locally
1. Create conf.toml
```bash
cp template.conf conf.toml
```
2. Fill your conf.toml with your secrets
3. Install the dependencies
```bash
poetry install
```
3. Start the service
```bash
poetry run python3 main.py
```