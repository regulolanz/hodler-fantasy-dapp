// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Importing required contracts and interfaces
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.3.2/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.3.2/contracts/access/AccessControl.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.3.2/contracts/security/Pausable.sol";
import "https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./playerRegistration.sol";  // Importing the playerRegistration contract

// Main PlayerCard contract
contract PlayerCard is ERC721Enumerable, AccessControl, Pausable {
    
    // Role definitions for access control
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    // Player Card Structure
    struct Card {
        address playerAddress;
        string team;
        string position; 
        string league;
        string season;
        string profilePicture; // This is an IPFS hash or URL pointing to the actual image
        uint256 fantasyPoints;
        bool isActive;
        uint256 salePrice; // Sale price for the card
    }

    // Mapping from card ID to Card details
    mapping(uint256 => Card) public cards;
    mapping(address => uint256) public playerToMintedCount;

    // Chainlink price feed for accurate ETH pricing
    AggregatorV3Interface internal priceFeed;
    
    // Reference to the PlayerRegistration contract
    PlayerRegistration playerRegistry;

    uint256 public constant MINTING_FEE_IN_USD = 50;

    // Array to store all minted card IDs
    uint256[] public allCardIds;

    // Events to notify frontend applications
    event CardMinted(address indexed player, uint256 cardId);
    event CardPurchased(address indexed buyer, uint256 cardId, uint256 salePrice);
    event FantasyPointsUpdated(uint256 cardId, uint256 newFantasyPoints);

    // Modifier for admin-only functions
    modifier onlyAdmin() {
        require(hasRole(ADMIN_ROLE, msg.sender), "Not an admin");
        _;
    }

    // Constructor to initialize contract
    constructor(address _priceFeed, address _playerRegistry) ERC721("PlayerCard", "PCARD") {
        priceFeed = AggregatorV3Interface(_priceFeed);
        playerRegistry = PlayerRegistration(_playerRegistry);

        // Setup roles
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(ADMIN_ROLE, msg.sender);
    }

     // Function to mint a new player card
    function mintCard(string memory team, string memory position, string memory league, string memory season, string memory profilePicture, uint256 fantasyPoints) public payable whenNotPaused {
        require(playerRegistry.isPlayerRegistered(msg.sender), "Player is not registered");
        
        uint256 currentEthPriceInUsd = getCurrentPrice();
        uint256 requiredFeeInEth = (MINTING_FEE_IN_USD * 1 ether) / currentEthPriceInUsd;

        require(msg.value == requiredFeeInEth, "Incorrect minting fee sent");

        // Update the player's minted card count
        playerToMintedCount[msg.sender]++;

        // Construct the new card ID
        uint256 playerNumber = playerRegistry.getPlayerNumber(msg.sender);
        uint256 newCardId = playerNumber * 1e6 + playerToMintedCount[msg.sender];  // This gives IDs in the format of 1-1, 1-2, 2-1, etc.

        cards[newCardId] = Card({
            playerAddress: msg.sender,
            team: team,
            position: position,
            league: league,
            season: season,
            profilePicture: profilePicture,
            fantasyPoints: fantasyPoints,
            isActive: true,
            salePrice: 0
        });

        allCardIds.push(newCardId);  // Store the card ID

        _mint(msg.sender, newCardId);
        emit CardMinted(msg.sender, newCardId);

        payable(msg.sender).transfer(msg.value);  // Refund any extra sent ether
    }

    // Function to retrieve all minted card IDs
    function getAllCardIds() external view returns (uint256[] memory) {
        return allCardIds;
    }

    // Function to set a sale price for a player card
    function setSalePrice(uint256 cardId, uint256 price) public {
        require(ownerOf(cardId) == msg.sender, "Not the owner of the card");
        cards[cardId].salePrice = price;
    }

    // Function for a user to purchase a card
    function buyCard(uint256 cardId) public payable whenNotPaused {
        require(cards[cardId].salePrice > 0, "Card is not for sale");
        require(msg.value == cards[cardId].salePrice, "Incorrect amount sent");

        address previousOwner = ownerOf(cardId);
        _transfer(previousOwner, msg.sender, cardId);

        payable(previousOwner).transfer(msg.value);
        emit CardPurchased(msg.sender, cardId, cards[cardId].salePrice);

        cards[cardId].salePrice = 0; // Reset the sale price
    }

    // Admin function to update fantasy points of a card
    function updateFantasyPoints(uint256 cardId, uint256 newPoints) public onlyAdmin {
        cards[cardId].fantasyPoints = newPoints;
        emit FantasyPointsUpdated(cardId, newPoints);
    }

    // Batch update function for admin to update multiple cards' fantasy points
    function updateFantasyPointsBatch(uint256[] memory cardIds, uint256[] memory newPoints) public onlyAdmin {
        require(cardIds.length == newPoints.length, "Mismatched arrays");

        for (uint256 i = 0; i < cardIds.length; i++) {
            cards[cardIds[i]].fantasyPoints = newPoints[i];
            emit FantasyPointsUpdated(cardIds[i], newPoints[i]);
        }
    }

    // Function to get the current ETH price from Chainlink oracle
    function getCurrentPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price);
    }

    // Function to calculate the minting fee in ETH based on current ETH price
    function calculateMintingFee() public view returns (uint256) {
        uint256 currentEthPriceInUsd = getCurrentPrice();
        return (MINTING_FEE_IN_USD * 1e18) / currentEthPriceInUsd;
    }

    // Overridden function to ensure compatibility with ERC721Enumerable and AccessControl
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721Enumerable, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}

