rm -rf site-parser/
unzip site-parser.zip -d site-parser/
cd site-parser
docker stop site-parser-container
docker rm site-parser-container
docker build -t site-parser .
docker run -d --name site-parser-container --restart=unless-stopped site-parser