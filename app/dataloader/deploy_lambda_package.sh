rm -rf v-env
rm -f MovieDataLoaderFunction.zip

virtualenv v-env
source v-env/bin/activate
pip3 install --prefix= -r requirements.txt
deactivate

cd v-env/lib/python3.6/site-packages
zip -r9 ${OLDPWD}/MovieDataLoaderFunction.zip .
cd $OLDPWD
zip -g MovieDataLoaderFunction.zip *.py

aws s3 cp MovieDataLoaderFunction.zip s3://$(aws cloudformation describe-stacks --stack-name movies-bucket --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)

aws lambda update-function-code \
--function-name $(aws cloudformation describe-stacks --stack-name movie-data-app-infra --query "Stacks[0].Outputs[?OutputKey=='MovieDataLoaderFunction'].OutputValue" --output text) \
--s3-bucket $(aws cloudformation describe-stacks --stack-name movies-bucket --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text) \
--s3-key MovieDataLoaderFunction.zip \
--publish

rm -rf v-env
rm -f MovieDataLoaderFunction.zip