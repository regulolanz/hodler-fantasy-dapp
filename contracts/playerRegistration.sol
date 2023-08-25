// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract PlayerRegistration is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant REGISTRAR_ROLE = keccak256("REGISTRAR_ROLE");

    // Structure to store Player's information
    struct PlayerInfo {
        string ipfsHash;      // IPFS hash containing player's personal details
        bool isRegistered;    // Flag to check if the player is registered
        bool isWaitlisted;    // Flag to check if the player is on the waitlist
    }

    // Mapping from player's address to their information
    mapping(address => PlayerInfo) public playerInfos;

    // Events
    event PlayerWaitlisted(address indexed playerAddress);
    event PlayerRegistered(address indexed playerAddress, string ipfsHash);
    event PlayerDeregistered(address indexed playerAddress);
    event PlayerRemovedFromWaitlist(address indexed playerAddress);

    modifier onlyAdmin() {
        require(hasRole(ADMIN_ROLE, msg.sender), "Not an admin");
        _;
    }

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(ADMIN_ROLE, msg.sender);
    }

    // Add an address to the waitlist
    function addToWaitlist(address playerAddress) public onlyAdmin {
        require(!playerInfos[playerAddress].isRegistered, "Player is already registered");
        playerInfos[playerAddress].isWaitlisted = true;
        _setupRole(REGISTRAR_ROLE, playerAddress);
        emit PlayerWaitlisted(playerAddress);
    }

    // Remove an address from the waitlist
    function removeFromWaitlist(address playerAddress) public onlyAdmin {
        require(playerInfos[playerAddress].isWaitlisted, "Player is not on the waitlist");
        playerInfos[playerAddress].isWaitlisted = false;
        revokeRole(REGISTRAR_ROLE, playerAddress);
        emit PlayerRemovedFromWaitlist(playerAddress);
    }

    // Register a player - Can only be done if they are on the waitlist
    function registerPlayer(string memory ipfsHash) public {
        require(hasRole(REGISTRAR_ROLE, msg.sender), "Not on the waitlist");
        require(playerInfos[msg.sender].isWaitlisted, "Player is not on the waitlist");
        require(!playerInfos[msg.sender].isRegistered, "Player is already registered");
        require(bytes(ipfsHash).length > 0, "IPFS hash cannot be empty");

        playerInfos[msg.sender] = PlayerInfo({
            ipfsHash: ipfsHash,
            isRegistered: true,
            isWaitlisted: false
        });

        revokeRole(REGISTRAR_ROLE, msg.sender);
        emit PlayerRegistered(msg.sender, ipfsHash);
    }

    function deregisterPlayer(address playerAddress) public onlyAdmin {
        require(playerInfos[playerAddress].isRegistered, "Player is not registered");
        playerInfos[playerAddress].isRegistered = false;
        emit PlayerDeregistered(playerAddress);
    }

    function isPlayerRegistered(address playerAddress) public view returns (bool) {
        return playerInfos[playerAddress].isRegistered;
    }

    // Function to get player's IPFS hash
    function getPlayerInfoHash(address playerAddress) public view returns (string memory) {
        return playerInfos[playerAddress].ipfsHash;
    }
}
