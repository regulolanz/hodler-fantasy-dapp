// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract PlayerRegistration is Ownable {
    // Structure to store Player's information
    struct PlayerInfo {
        string ipfsHash; // IPFS hash containing player's personal details
        bool isRegistered;
    }

    // Mapping from player's address to their information
    mapping(address => PlayerInfo) public playerInfos;

    // Mapping to keep track of waitlisted addresses
    mapping(address => bool) public isWaitlisted;

    event PlayerWaitlisted(address indexed playerAddress);
    event PlayerRegistered(address indexed playerAddress, string ipfsHash);
    event PlayerDeregistered(address indexed playerAddress);

    // Add an address to the waitlist
    function addToWaitlist(address playerAddress) public onlyOwner {
        require(!isWaitlisted[playerAddress], "Player is already waitlisted");
        isWaitlisted[playerAddress] = true;
        emit PlayerWaitlisted(playerAddress);
    }

    // Remove an address from the waitlist
    function removeFromWaitlist(address playerAddress) public onlyOwner {
        require(isWaitlisted[playerAddress], "Player is not waitlisted");
        isWaitlisted[playerAddress] = false;
    }

    // Register a player - Can only be done if they are on the waitlist
    function registerPlayer(address playerAddress, string memory ipfsHash) public onlyOwner {
        require(isWaitlisted[playerAddress], "Player is not on the waitlist");
        PlayerInfo storage player = playerInfos[playerAddress];
        require(!player.isRegistered, "Player is already registered");

        player.ipfsHash = ipfsHash;
        player.isRegistered = true;
        
        // Optionally, once registered, you can remove them from the waitlist
        isWaitlisted[playerAddress] = false;

        emit PlayerRegistered(playerAddress, ipfsHash);
    }

    function deregisterPlayer(address playerAddress) public onlyOwner {
        PlayerInfo storage player = playerInfos[playerAddress];
        require(player.isRegistered, "Player is not registered");

        player.isRegistered = false;
        emit PlayerDeregistered(playerAddress);
    }

    function isPlayerRegistered(address playerAddress) public view returns (bool) {
        return playerInfos[playerAddress].isRegistered;
    }

    // Function to get player's IPFS hash, might be used by other contracts or DApps
    function getPlayerInfoHash(address playerAddress) public view returns (string memory) {
        return playerInfos[playerAddress].ipfsHash;
    }
}


// Note:
    // The IPFS hash contains the detailed form information of the player (Name, Last Name, Nationality, DOB, Email, Phone, Address (ENS Domain), and Selfie).
    // A player can be registered only if they are on the waitlist. Once registered, they can optionally be removed from the waitlist.
    // Personal data like emails, phone numbers, addresses, and selfies should be treated with care, and the IPFS content should probably be encrypted. Handling this data requires careful consideration due to privacy concerns and GDPR compliance.
    // Next, you can proceed to integrate this contract with the rest of your dApp components, ensuring you maintain the utmost data security and compliance standards throughout the application.