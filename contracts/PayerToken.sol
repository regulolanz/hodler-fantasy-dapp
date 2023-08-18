// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract PlayerToken is ERC721Enumerable {
    using Counters for Counters.Counter;
    using SafeMath for uint256;

    Counters.Counter private _tokenIdCounter;
    uint256 public constant PRICE_IN_ETH = 0.025 ether; // Placeholder for $50 in ETH. This should be dynamic.

    struct PlayerAttributes {
        string playerName;
        string playerLastName;
        string team;
        string position;
        string league;
        string season;
        string nationality;
        uint yearOfBirth;
        uint256 fantasyPoints;
    }

    mapping(uint256 => string) private _tokenURIs;
    mapping(uint256 => PlayerAttributes) public playerAttributes;

    constructor() ERC721("PlayerToken", "PLAYR") {}

    function mint(address player, string memory tokenURI, PlayerAttributes memory attributes) public payable returns (uint256) {
        require(msg.value == PRICE_IN_ETH, "Incorrect ETH amount sent");
        
        _tokenIdCounter.increment();
        uint256 newTokenId = _tokenIdCounter.current();
        _safeMint(player, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        playerAttributes[newTokenId] = attributes;

        return newTokenId;
    }

    function mintMultiple(address[] memory players, string[] memory tokenURIs, PlayerAttributes[] memory attributesList) public payable returns (uint256[] memory) {
        require(players.length == tokenURIs.length && tokenURIs.length == attributesList.length, "Input arrays length mismatch");
        require(msg.value == PRICE_IN_ETH.mul(players.length), "Incorrect ETH amount sent");

        uint256[] memory tokenIds = new uint256[](players.length);

        for (uint256 i = 0; i < players.length; i++) {
            _tokenIdCounter.increment();
            uint256 newTokenId = _tokenIdCounter.current();
            _safeMint(players[i], newTokenId);
            _setTokenURI(newTokenId, tokenURIs[i]);
            playerAttributes[newTokenId] = attributesList[i];
            tokenIds[i] = newTokenId;
        }

        return tokenIds;
    }

    function _setTokenURI(uint256 tokenId, string memory _tokenURI) internal virtual {
        _tokenURIs[tokenId] = _tokenURI;
    }

    function updateFantasyPoints(uint256 tokenId, uint256 points) public {
        PlayerAttributes storage attributes = playerAttributes[tokenId];
        attributes.fantasyPoints += points;
    }
}
