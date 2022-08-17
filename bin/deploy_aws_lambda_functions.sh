# create deployment file
echo $1
for i in `ls ../src`;
do
echo $i
cd ../src/$i
zip -r9 $i.zip .

mv ./$i.zip ../../dist/$i.zip
cd ../../bin

# create lambda function or update code
aws lambda create-function \
    --function-name $i \
    --runtime python3.9 \
    --zip-file fileb://../dist/$i.zip \
    --handler lambda_handler.lambda_handler \
    --role arn:aws:iam::592336536196:role/service-role/ims-dev-iam-role-organization || \
    aws lambda update-function-code \
    --function-name  $i \
    --zip-file fileb://../dist/$i.zip
done;