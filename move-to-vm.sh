rm site-parser.zip
zip -r site-parser . -x ".git*" "site-parser.zip" "root.crt" ".DS_Store" "draft*" "venv*" "__pycache__*"
scp site-parser.zip resul@84.201.177.37:~/
scp deploy-site-parser.sh resul@84.201.177.37:~/

ssh resul@84.201.177.37