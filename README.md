## hodler-fantasy-dapp

A decentralized fantasy soccer platform powered by Ethereum and IPFS. Users can build dynamic teams using tokenized players, represented as Dynamic NFTs. These Dynamic NFTs, in the form of player cards, can have their fantasy points updated post each game, mirroring the real-world performance of the players.

## Table of Contents

1. [Project Description](#project-description)
2. [Technologies and Tools Used](#technologies-and-tools-used)
3. [Application Flow](#application-flow)
4. [Roles and Permissions in the PlayerRegistration Contract](#roles-and-permissions-in-the-playerregistration-contract)
5. [Media Illustrations](#media-illustrations)
6. [Quick Start & Configuration](#quick-start-and-configuration)
7. [Feedback](#feedback)

## Project Description

The `hodler-fantasy-dapp` offers a blend of fantasy soccer and blockchain technology. Users own, trade, and compete using tokenized player cards. These cards are not static; their value and attributes (like fantasy points) can change based on real-world events, thanks to integration with Chainlink oracles.

## Technologies and Tools Used

- **Blockchain**:
  - **Solidity**: The smart contracts for the platform are written in Solidity.
  - **Ethereum**: The decentralized platform where the smart contracts are deployed.
  - **Chainlink**: Used as an oracle to fetch external data into the smart contracts.
  - **IPFS**: Utilized for decentralized storage of player data.

- **Backend & Data Handling**:
  - **Python**: Powers the backend of the platform.
  - **Streamlit**: Offers a UI for user interactions.
  - **Jupyter Notebook**: Used for development and data analysis.

- **Cloud & External Services**:
  - **AWS**: Provides cloud services, including S3 for storage and API Gateway for data access.
  - **Infura**: Offers Ethereum node infrastructure.

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
   - Through the Streamlit interface, the admin can query this data directly from the S3 bucket via an AWS API Gateway endpoint.
   - The retrieved fantasy points are then updated on the Ethereum blockchain for the respective player cards.

## Media Illustrations

This section provides visual aids to understand deployment and user interactions:

- [Deploying PlayerRegistration Contract](resources/images/PlayerRegistration_Deploy.png)
- [Deploying PlayerCard Contract](resources/images/PlayerCard_Deploy.png)
- [Player Registration in Streamlit Video](resources/videos/Player_Registration_Streamlit.mp4)
- [Mint Player Card in Streamlit Video](resources/videos/Mint_PlayerCard_Streamlit.mp4)
- [Updating Fantasy Points in Streamlit Video](resources/videos/Update_Fantasy_Points.mp4)
- [Screenshot of Updated Fantasy Points](resources/images/FantasyPoints_Updated.png)

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

## Quick Start & Configuration

- **Prerequisites**: Basic knowledge of blockchain, Ethereum, and Python. Ensure that you have necessary tools like `Node.js`, `Python`, etc.
- **Setup**:
  1. Clone the repository.
  2. Install the necessary dependencies.
  3. Configure settings in the `.env` file and `.streamlit` folder as per your needs.

Note: Detailed configurations and environment settings have been intentionally left out to maintain the uniqueness of the project. For specific configurations or collaborations, please reach out to the project maintainers.

## Feedback

We value your feedback! If you have suggestions or find any issues, please report them. While we might not respond to each feedback entry, be assured that we regularly review the inputs and work on improving the platform.

