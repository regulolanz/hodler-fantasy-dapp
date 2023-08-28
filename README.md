# hodler-fantasy-dapp

A decentralized fantasy soccer platform powered by Ethereum and IPFS. Users can build dynamic teams using tokenized players, represented as Dynamic NFTs. These Dynamic NFTs, in the form of player cards, can have their fantasy points updated post each game, mirroring the real-world performance of the players.

## Table of Contents

1. [Project Description](#project-description)
   - [Smart Contracts](#smart-contracts)
     - [`playerRegistration.sol`](#playerregistrationsol)
     - [`playerCard.sol`](#playercardsol)
   - [Backend Service: `app.py`](#backend-service-apppy)
   
2. [Application Flow](#application-flow)

3. [Setting Up and Deploying Smart Contracts](#setting-up-and-deploying-smart-contracts-using-ganache-and-remix)
   - [Install nvm (Node Version Manager)](#install-nvm-node-version-manager)
   - [Install Ganache](#install-ganache)
   - [Setting up Infura](#setting-up-infura)
   - [Run Ganache with Infura](#run-ganache-with-infura)
   - [Deploying Contracts with Remix](#deploying-contracts-with-remix)

4. [Deployment Media](#deployment-media)
   - [Deploying Smart Contracts](#deploying-smart-contracts)
   - [Streamlit Interface Interactions](#streamlit-interface-interactions)

5. [Roles and Permissions in the PlayerRegistration Contract](#roles-and-permissions-in-the-playerregistration-contract)

6. [Configuration File Explanation (`SAMPLE.env`)](#configuration-file-explanation-sampleenv)

7. [Setup AWS Services (API Gateway and S3)](#setup-aws-services-api-gateway-and-s3)
   - [Setting up S3 Bucket](#setting-up-s3-bucket)
   - [Setting up API Gateway](#setting-up-api-gateway)

## Project Description

The `hodler-fantasy-dapp` offers a blend of fantasy soccer and blockchain technology. Users own, trade, and compete using tokenized player cards. These cards are not static; their value and attributes (like fantasy points) can change based on real-world events, thanks to integration with Chainlink oracles.

### Smart Contracts:

#### 1. `playerRegistration.sol`:

- **Purpose**: Manages the registration of players on the platform.
- **Key Features**:
  - Add players to a waitlist.
  - Register players on the waitlist using their IPFS-stored personal details.
  - Role-based management for registrations.
  
#### 2. `playerCard.sol`:

- **Purpose**: Tokenizes players into dynamic NFTs (player cards) and manages the attributes of each card.
- **Key Features**:
  - Mint new player cards for registered players.
  - Update fantasy points of the cards, making them dynamic.
  - List player cards for sale and allow purchases.
  - Integrate with Chainlink oracles for current ETH price for minting fee calculations.

### Backend Service:

#### `app.py`:

- **Purpose**: Serves as the backend, interfacing with Ethereum to facilitate user interactions.
- **Key Features**:
  - Register players, capturing their details and selfie.
  - UI for minting player cards.
  - Interaction with smart contracts using `web3.py`.
  - Integration with IPFS through `pinata` for off-chain data storage.

---

## Application Flow

1. **Player Registration**: 
   - Players, once waitlisted by the admin, can register themselves through the Streamlit interface.
   - They need to provide personal details and upload a selfie.
   - This data is stored on IPFS, and only the hash of this data is stored on the Ethereum blockchain to ensure data integrity and privacy.

2. **Minting Player Cards**: 
   - Once registered, players can mint their own player cards.
   - These cards represent the player's profile as NFTs on the blockchain.
   - Fantasy points are initialized to zero during minting and can be updated later based on player performance.

3. **Updating Fantasy Points**: 
   - After every game, an external system updates the fantasy points of the players based on their performance.
   - This data is then stored in an S3 bucket in a JSON format.
   - Through the Streamlit interface, the admin can trigger a Chainlink oracle to fetch the updated fantasy points for players from the S3 bucket and update the respective player cards on the Ethereum blockchain.

---

## Deployment and Setup

This section guides you through the deployment of smart contracts and the setup of various tools and services required.

### Setting Up and Deploying Smart Contracts using Ganache and Remix

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

---

## Media Illustrations

This section provides visual aids to understand deployment and user interactions:

- [Deploying PlayerRegistration Contract](resources/images/PlayerRegistration_Deploy.png)
- [Deploying PlayerCard Contract](resources/images/PlayerCard_Deploy.png)
- [Player Registration in Streamlit Video](resources/videos/Player_Registration_Streamlit.mp4)
- [Mint Player Card in Streamlit Video](resources/videos/Mint_PlayerCard_Streamlit.mp4)

---

## Roles and Permissions

Details on roles and permissions in the `PlayerRegistration` contract.

- **DEFAULT_ADMIN_ROLE or ADMIN_ROLE**:
  - Add or remove addresses from the waitlist.
  - Deregister players.

- **REGISTRAR_ROLE**:
  - Register themselves as players.
  - Lose the `REGISTRAR_ROLE` after registration.

- **No Role**:
  - View data without special functionality.

---

## Configuration File Explanation (`SAMPLE.env`)

This section explains the environment variables needed for the backend service.

1. **PINATA_API_KEY**: Your Pinata service API key.
2. **PINATA_SECRET_API_KEY**: The secret key for the above API key.
3. **WEB3_PROVIDER_URI**: URI of your Ethereum node provider.
4. **PLAYER_REGISTRATION_CONTRACT_ADDRESS**: Ethereum address of the deployed `playerRegistration.sol` contract.
5. **PLAYER_CARD_CONTRACT_ADDRESS**: Ethereum address of the deployed `playerCard.sol` contract.

---

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