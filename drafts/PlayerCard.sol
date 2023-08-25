// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./PlayerRegistration.sol"; // Import PlayerRegistration contract

contract PlayerCard is ERC721Enumerable, AccessControl {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant UPDATER_ROLE = keccak256("UPDATER_ROLE");

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
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(UPDATER_ROLE, msg.sender);
        
        playerRegistration = PlayerRegistration(_playerRegistrationAddress);
    }
    
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721Enumerable, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
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

    function endSeasonMinting() external onlyRole(DEFAULT_ADMIN_ROLE) {
        canMint = false;
    }

    function updateFantasyPoints(uint256 tokenId, uint256 points) external onlyRole(UPDATER_ROLE) {
        require(cards[tokenId].isActive, "This card is from a previous season");
        
        cards[tokenId].fantasyPoints += points;

        // Reward logic can be added here. 
        // e.g., rewardTokenContract.mint(cards[tokenId].playerAddress, points);
    }
}
