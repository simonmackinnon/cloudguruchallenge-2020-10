# cloudguruchallenge-2020-10

See the background details here:
[https://acloudguru.com/blog/engineering/cloudguruchallenge-machine-learning-on-aws](https://acloudguru.com/blog/engineering/cloudguruchallenge-machine-learning-on-aws)

Basic steps to create the whole stack:
* Deploy /infra/01_s3-bucket.yaml stack
* Run the /app/dataloader and app/recommender function deployment scripts
* change the bucket name and change sagemaker execution role arn in /app/modelcreation/imdb_data_analyse.ipynb
* Run the Jupyter notebook /app/modelcreation/imdb_data_analyse.ipynb
* Deploy /infra/02_core-app-infrastructure.yaml stack
* Run the MovieDataLoader function (invoke manually)
* Deploy /infra/03_recommender-api.yaml stack
* Deploy /infra/04_s3-site-and-cdn.yaml stack
* Build the React website /app/site/moviesfinder
* Deploy website to s3 bucket (created in /infra/04_s3-site-and-cdn.yaml stack)
* Invalidate CDN (if needed)