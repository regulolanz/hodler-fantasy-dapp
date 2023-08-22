// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./PlayerRegistration.sol"; // Import PlayerRegistration contract

contract PlayerCard is ERC721Enumerable, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    PlayerRegistration public playerRegistration; // Reference to the PlayerRegistration contract

    struct Card {
        address playerAddress;
        string team;
        string position; 
        string league;
        string season;
        string profilePicture;
        uint256 fantasyPoints;
        bool isActive;
    }

    mapping(uint256 => Card) public cards;
    bool public canMint = true;

    modifier onlyRegisteredPlayer() {
        require(playerRegistration.isPlayerRegistered(msg.sender), "Not a registered player");
        _;
    }

    constructor(address _playerRegistrationAddress) ERC721("PlayerCard", "PCARD") {
        playerRegistration = PlayerRegistration(_playerRegistrationAddress);
    }

    function mintCard(string memory team, string memory position, string memory league, string memory season, string memory profilePicture) external onlyRegisteredPlayer {
        require(canMint, "Minting has ended for this season");
        
        uint256 newTokenId = _tokenIdCounter.current();
        cards[newTokenId] = Card({
            playerAddress: msg.sender,
            team: team,
            position: position,
            league: league,
            season: season,
            profilePicture: profilePicture,
            fantasyPoints: 0,
            isActive: true
        });
        
        _mint(msg.sender, newTokenId);
        _tokenIdCounter.increment();
    }

    function endSeasonMinting() external onlyOwner {
        canMint = false;
    }

    function updateFantasyPoints(uint256 tokenId, uint256 points) external onlyOwner {
        require(cards[tokenId].isActive, "This card is from a previous season");
        
        cards[tokenId].fantasyPoints += points;

        // Reward H3 tokens logic here. 
        // For this, you need to integrate with your H3 token contract. 
        // e.g., h3TokenContract.mint(cards[tokenId].playerAddress, points);
    }
}