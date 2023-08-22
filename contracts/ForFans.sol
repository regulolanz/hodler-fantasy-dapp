// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ForFans is Ownable {
    IERC721 public playerToken; // Reference to the PlayerToken contract
    IERC20 public hodlerToken;  // Reference to the HodlerToken contract

    struct Fan {
        string name;
        string lastName;
        string nationality;
        uint256 DOB;
        string email;
        string phone;
        string addressENS;
        string selfie;
        bool isRegistered;
        uint256 earnedH3Tokens;
        uint256 fantasyPoints;
    }

    // Mapping to store fan information
    mapping(address => Fan) public fans;

    // Mapping to store the fan's custom card prices
    mapping(uint256 => mapping(address => uint256)) public fanCardPrices;

    uint256 public cardPrice; // Default card price in H3 Tokens
    uint256 public creatorFeePercentage; // Creator fee percentage

    // Event to log card purchase
    event CardPurchased(address indexed buyer, uint256 tokenId, uint256 price, bool useHodlerToken);

    // Event to log card price update
    event CardPriceUpdated(uint256 tokenId, address indexed owner, uint256 newPrice);

    constructor(address _playerTokenAddress, address _hodlerTokenAddress, uint256 _cardPrice) {
        playerToken = IERC721(_playerTokenAddress);
        hodlerToken = IERC20(_hodlerTokenAddress);
        cardPrice = _cardPrice;
        creatorFeePercentage = 5; // 5% creator fee by default
    }

    // Modifier to ensure only registered fans can access certain functions
    modifier onlyFan() {
        require(fans[msg.sender].isRegistered, "Only registered fans can call this function");
        _;
    }

    // Function for fans to register
    function registerAsFan(
        string memory _name,
        string memory _lastName,
        string memory _nationality,
        uint256 _DOB,
        string memory _email,
        string memory _phone,
        string memory _addressENS,
        string memory _selfie
    ) external {
        fans[msg.sender] = Fan({
            name: _name,
            lastName: _lastName,
            nationality: _nationality,
            DOB: _DOB,
            email: _email,
            phone: _phone,
            addressENS: _addressENS,
            selfie: _selfie,
            isRegistered: true,
            earnedH3Tokens: 0,
            fantasyPoints: 0
        });
    }

    // Function for fans to buy player cards
    function buyPlayerCard(uint256 _tokenId, bool useHodlerToken) external payable {
        require(playerToken.ownerOf(_tokenId) != address(0), "Invalid player card token");
        require(playerToken.getApproved(_tokenId) == address(this), "Contract not approved to transfer");

        uint256 price = fanCardPrices[_tokenId][msg.sender];
        if (price == 0) {
            price = cardPrice;
        }

        if (useHodlerToken) {
            // Ensure that the fan has enough H3 Tokens to buy the card
            require(hodlerToken.balanceOf(msg.sender) >= price, "Insufficient H3 Tokens");
            // Transfer the card price in H3 Tokens to the player
            hodlerToken.transferFrom(msg.sender, playerToken.ownerOf(_tokenId), price);
        } else {
            // Ensure that the fan has sent enough Ether to buy the card
            require(msg.value >= price, "Insufficient Ether");
            // Transfer the Ether to the player
            payable(playerToken.ownerOf(_tokenId)).transfer(price);
        }

        // Transfer the player card to the fan
        playerToken.safeTransferFrom(playerToken.ownerOf(_tokenId), msg.sender, _tokenId);

        // Emit the CardPurchased event
        emit CardPurchased(msg.sender, _tokenId, price, useHodlerToken);
    }

    // Function for fans to set their own card price for a specific token
    function setCardPrice(uint256 _tokenId, uint256 _price) external onlyFan {
        fanCardPrices[_tokenId][msg.sender] = _price;

        // Emit the CardPriceUpdated event
        emit CardPriceUpdated(_tokenId, msg.sender, _price);
    }

    // Function to calculate the creator fee for a card sale
    function calculateCreatorFee(uint256 _salePrice) internal view returns (uint256) {
        return (_salePrice * creatorFeePercentage) / 100;
    }

    // Function to sell a player card with a new price
    function sellPlayerCard(uint256 _tokenId, uint256 _newPrice) external onlyFan {
        address cardOwner = playerToken.ownerOf(_tokenId);
                require(fanCardPrices[_tokenId][msg.sender] > 0, "You do not own this card");
        
        // Calculate the creator fee
        uint256 creatorFee = (_newPrice * 5) / 100;

        // Transfer the creator fee to the contract owner
        payable(owner()).transfer(creatorFee / 2);

        // Transfer 50% of the creator fee to the player (original owner of the card)
        fans[cardOwner].earnedH3Tokens += creatorFee / 2;

        // Update the card's price
        fanCardPrices[_tokenId][msg.sender] = _newPrice;
    }

    // Function to update the creator fee percentage (only owner)
    function updateCreatorFeePercentage(uint256 _newPercentage) external onlyOwner {
        require(_newPercentage <= 100, "Percentage must be <= 100");
        creatorFeePercentage = _newPercentage;
    }

    // Fallback function to receive Ether
    receive() external payable {}

    // Fallback function to receive tokens
    function tokenFallback(address _from, uint256 _value) external {}
}