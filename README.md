<h1 align="center">
  <img src="static/Images/horizon24.gif"/><br />
  Horizon'24 | ACM-SIST
</h1>

<p align="center">Backend for Horizon'2024 at Sathyabama developed by ACM-SIST Student Chapter</p>


## Setup

Required: <b>Python >= 3.10</b>

### Install Requirements
```bash
pip install -r requirements.txt
```

### Configuration
Create the file called `.env` in the root directory of the project and set the values for the below environment variables
```plaintext
MONGODB_URL=
MAIL_USER=
MAIL_PASS=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
CLOUDINARY_CLOUD_NAME=
ADMIN_PASSWORD=
ACCESS_TOKEN_EXPIRE_DAYS=2
SECRET_KEY=
DOMAIN=
FRONTEND_DOMAIN=
```
<b>NOTE</b>: <EMAIL_PASSWORD> is the App Password. Please refer this [link](https://support.google.com/accounts/answer/185833?hl=en) to create App Password

### Run the server
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/kishor1445/ACM_SIST_Backend/blob/v2/LICENSE) file for more details.
