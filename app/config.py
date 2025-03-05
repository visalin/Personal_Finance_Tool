import os
from dotenv import load_dotenv
import boto3
from botocore.config import Config as BotoConfig

load_dotenv()

class Config:
    # Get base directory of the application
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # Certificate path
    SSL_CA = os.path.join(BASEDIR, 'certs', 'rds-ca-2019-root.pem')

    # AWS and Database Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
    DB_USER = os.environ.get('DB_USER')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME')

    def get_db_auth_token(self):
        try:
            # Explicitly configure boto3 with region
            boto_config = BotoConfig(
                region_name=self.AWS_REGION
            )
            
            # Create RDS client with explicit region configuration
            rds_client = boto3.client(
                'rds',
                region_name=self.AWS_REGION,
                config=boto_config
            )
            
            auth_token = rds_client.generate_db_auth_token(
                DBHostname=self.DB_HOST,
                Port=int(self.DB_PORT),
                DBUsername=self.DB_USER,
                Region=self.AWS_REGION
            )
            return auth_token
        except Exception as e:
            print(f"Error generating auth token: {str(e)}")
            return None

    # Database URI configuration
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{os.environ.get('DB_PASSWORD')}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?ssl_ca={SSL_CA}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
