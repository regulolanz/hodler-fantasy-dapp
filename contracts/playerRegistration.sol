// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Importing the AccessControl contract from OpenZeppelin for role-based access control
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.3.2/contracts/access/AccessControl.sol";

// PlayerRegistration Contract
contract PlayerRegistration is AccessControl {

    // Role Definitions
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant REGISTRAR_ROLE = keccak256("REGISTRAR_ROLE");

    // Keeping track of player numbers
    uint256 public lastPlayerNumber = 0;  // This will keep track of the last issued player number

    // Structure to store Player's information
    struct PlayerInfo {
        uint256 playerNumber;       // Unique player number
        string ipfsHash;            // IPFS hash containing player's personal details
        bool isRegistered;          // Flag to check if the player is registered
        bool isWaitlisted;          // Flag to check if the player is on the waitlist
    }

    // Mapping from player's address to their information
    mapping(address => PlayerInfo) public playerInfos;

    // Events for logging important actions
    event PlayerWaitlisted(address indexed playerAddress);
    event PlayerRegistered(address indexed playerAddress, string ipfsHash);
    event PlayerDeregistered(address indexed playerAddress);
    event PlayerRemovedFromWaitlist(address indexed playerAddress);

    // Modifier to restrict access to admin-only functions
    modifier onlyAdmin() {
        require(hasRole(ADMIN_ROLE, msg.sender), "Not an admin");
        _;
    }

    // Constructor to initialize roles
    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(ADMIN_ROLE, msg.sender);
    }

    // Function to add an address to the waitlist
    function addToWaitlist(address playerAddress) public onlyAdmin {
        require(!playerInfos[playerAddress].isRegistered, "Player is already registered");
        require(!playerInfos[playerAddress].isWaitlisted, "Player is already on the waitlist");
        playerInfos[playerAddress].isWaitlisted = true;
        grantRole(REGISTRAR_ROLE, playerAddress);
        emit PlayerWaitlisted(playerAddress);
    }

    // Function to remove an address from the waitlist
    function removeFromWaitlist(address playerAddress) public onlyAdmin {
        require(playerInfos[playerAddress].isWaitlisted, "Player is not on the waitlist");
        playerInfos[playerAddress].isWaitlisted = false;
        _revokeRegistrarRole(playerAddress);
        emit PlayerRemovedFromWaitlist(playerAddress);
    }

    // Function to register a player - can only be done if they are on the waitlist
    function registerPlayer(string memory ipfsHash) public {
        require(playerInfos[msg.sender].isWaitlisted, "Player is not on the waitlist");
        require(!playerInfos[msg.sender].isRegistered, "Player is already registered");
        require(bytes(ipfsHash).length > 0, "IPFS hash cannot be empty");

        lastPlayerNumber += 1;  // Increment the player number

        playerInfos[msg.sender].playerNumber = lastPlayerNumber;
        playerInfos[msg.sender].ipfsHash = ipfsHash;
        playerInfos[msg.sender].isRegistered = true;
        playerInfos[msg.sender].isWaitlisted = false;

        _revokeRegistrarRole(msg.sender);
        emit PlayerRegistered(msg.sender, ipfsHash);
    }

    // Admin function to deregister a player
    function deregisterPlayer(address playerAddress) public onlyAdmin {
        require(playerInfos[playerAddress].isRegistered, "Player is not registered");
        playerInfos[playerAddress].isRegistered = false;
        emit PlayerDeregistered(playerAddress);
    }

    // Function to check if a player is registered
    function isPlayerRegistered(address playerAddress) public view returns (bool) {
        return playerInfos[playerAddress].isRegistered;
    }

    // Function to retrieve a player's IPFS hash
    function getPlayerInfoHash(address playerAddress) public view returns (string memory) {
        return playerInfos[playerAddress].ipfsHash;
    }

    // Function to get player number
    function getPlayerNumber(address playerAddress) public view returns (uint256) {
        return playerInfos[playerAddress].playerNumber;
    }
    
    // Custom revoke mechanism for REGISTRAR_ROLE with silent error handling
    function _revokeRegistrarRole(address account) internal {
        try this.revokeRole(REGISTRAR_ROLE, account) {
        } catch {
            // Handle any errors silently
        }
    }
}

