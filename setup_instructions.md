# Developer Setup Instructions for hodler-fantasy-dapp

This guide provides step-by-step instructions for setting up and deploying the `hodler-fantasy-dapp`.

## Table of Contents

1. [Setting Up and Deploying Smart Contracts using Ganache and Remix](#setting-up-and-deploying-smart-contracts-using-ganache-and-remix)
2. [Configuration File Explanation (`SAMPLE.env`)](#configuration-file-explanation-sampleenv)
3. [Setup AWS Services (API Gateway and S3)](#setup-aws-services-api-gateway-and-s3)

## Setting Up and Deploying Smart Contracts using Ganache and Remix

1. **Install nvm (Node Version Manager)**
  
   nvm lets you manage multiple Node.js versions.

   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
   ```

2. **Install Ganache**

   Ganache provides a personal Ethereum blockchain for local testing.

   ```bash
   npm install -g ganache-cli
   ```

3. **Setting up Infura**

   Infura offers a remote Ethereum node infrastructure.

   - Visit [Infura](https://infura.io/) and create a new account.
   - Create a new project to get your endpoint URL.

4. **Run Ganache with Infura**

   ```bash
   ganache-cli --fork=<INFURA_URL>
   ```

5. **Deploy Contracts with Remix**

   Use [Remix](https://remix.ethereum.org/) to deploy your smart contracts. 

## Configuration File Explanation (`SAMPLE.env`)

This section explains the environment variables needed for the backend service.

1. **PINATA_API_KEY**: Your Pinata service API key.
2. **PINATA_SECRET_API_KEY**: The secret key for the above API key.
3. **WEB3_PROVIDER_URI**: URI of your Ethereum node provider.
4. **PLAYER_REGISTRATION_CONTRACT_ADDRESS**: Ethereum address of the deployed `playerRegistration.sol` contract.
5. **PLAYER_CARD_CONTRACT_ADDRESS**: Ethereum address of the deployed `playerCard.sol` contract.

## Setup AWS Services (API Gateway and S3)

### Setting up S3 Bucket:

1. **Login to AWS**:
   - Navigate to the AWS Management Console.
   - Open the Amazon S3 console at [Amazon S3](https://console.aws.amazon.com/s3/).

2. **Create Bucket**:
   - Click `Create Bucket`.
   - Enter a unique DNS-compliant name for your new bucket.
   - Choose the region where you want the bucket to reside and click `Next`.
   - Keep the default settings and click `Next`.
   - Set your desired permissions and click `Next`.
   - Review your settings and click `Create Bucket`.

3. **Upload the JSON**:
   - Navigate to your newly created bucket.
   - Click `Upload`.
   - Drag and drop or choose your `hodlerfc.json` file and click `Upload`.

### Setting up API Gateway:

1. **Open API Gateway**:
   - Navigate to the AWS Management Console.
   - Open the API Gateway console at [API Gateway](https://console.aws.amazon.com/apigateway/).

2. **Create API**:
   - Click `Create API`.
   - Choose `REST API` and click `Build`.
   - Choose `New API` and provide a name and description. Click `Create API`.

3. **Configure Lambda Trigger**:
   - In the left navigation pane, click `Resources`.
   - Click `Create Resource` and provide a name and path.
   - Once the resource is created, click `Create Method` and choose `GET`.
   - In the setup pane, choose `Lambda Function` as the integration type.
   - Select the region where your Lambda function (`lambda.py`) resides and type the name of your Lambda function.
   - Click `Save`.

4. **Deploy API**:
   - In the Actions dropdown, click `Deploy API`.
   - Choose a deployment stage and click `Deploy`.
   - Note down the `Invoke URL` provided. This will be your API endpoint.

