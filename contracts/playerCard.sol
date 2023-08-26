// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.3.2/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.3.2/contracts/access/Ownable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.3.2/contracts/security/Pausable.sol";
import "https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./playerRegistration.sol";  // Import the playerRegistration contract

contract PlayerCard is ERC721Enumerable, Ownable, Pausable {

    struct Card {
        address playerAddress;
        string team;
        string position; 
        string league;
        string season;
        string profilePicture; // Consider this as an IPFS hash or URL pointing to the actual image
        uint256 fantasyPoints;
        bool isActive;
        uint256 salePrice; // Sale price for the card
    }

    mapping(uint256 => Card) public cards;
    AggregatorV3Interface internal priceFeed;
    PlayerRegistration playerRegistry; // The playerRegistration contract instance
    uint256 public constant MINTING_FEE_IN_USD = 50;

    event CardMinted(address indexed player, uint256 cardId);
    event CardPurchased(address indexed buyer, uint256 cardId, uint256 salePrice);
    event FantasyPointsUpdated(uint256 cardId, uint256 newFantasyPoints);

    constructor(address _priceFeed, address _playerRegistry) ERC721("PlayerCard", "PCARD") {
        priceFeed = AggregatorV3Interface(_priceFeed);
        playerRegistry = PlayerRegistration(_playerRegistry);
    }

    modifier onlyRegisteredPlayer(address _player) {
        require(playerRegistry.isPlayerRegistered(_player), "Player is not registered");
        _;
    }

    function mintCard(string memory team, string memory position, string memory league, string memory season, string memory profilePicture, uint256 fantasyPoints) public payable onlyRegisteredPlayer(msg.sender) whenNotPaused {
        uint256 currentEthPriceInUsd = getCurrentPrice();
        uint256 requiredFeeInEth = (MINTING_FEE_IN_USD * 1 ether) / currentEthPriceInUsd;

        require(msg.value == requiredFeeInEth, "Incorrect minting fee sent");

        uint256 newCardId = totalSupply() + 1;
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

        _mint(msg.sender, newCardId);
        emit CardMinted(msg.sender, newCardId);

        payable(owner()).transfer(msg.value); // Transfer the minting fee to the contract owner
    }

    function setSalePrice(uint256 cardId, uint256 price) public {
        require(ownerOf(cardId) == msg.sender, "Not the owner of the card");
        cards[cardId].salePrice = price;
    }

    function buyCard(uint256 cardId) public payable whenNotPaused {
        require(cards[cardId].salePrice > 0, "Card is not for sale");
        require(msg.value == cards[cardId].salePrice, "Incorrect amount sent");

        address previousOwner = ownerOf(cardId);
        _transfer(previousOwner, msg.sender, cardId);

        payable(previousOwner).transfer(msg.value);
        emit CardPurchased(msg.sender, cardId, cards[cardId].salePrice);

        cards[cardId].salePrice = 0; // Reset the sale price
    }

    function updateFantasyPoints(uint256 cardId, uint256 newPoints) public onlyOwner {
        cards[cardId].fantasyPoints = newPoints;
        emit FantasyPointsUpdated(cardId, newPoints);
    }

    function getCurrentPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price);
    }

    function calculateMintingFee() public view returns (uint256) {
    uint256 currentEthPriceInUsd = getCurrentPrice();
    return (MINTING_FEE_IN_USD * 1e18) / currentEthPriceInUsd;
    }
}
