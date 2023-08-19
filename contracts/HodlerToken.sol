// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract HodlerToken is ERC20, Ownable {
    constructor() ERC20("Hodler Token", "HODL") {
        // Mint an initial supply of tokens to the contract owner
        _mint(msg.sender, 1000000 * 10**18); // Mint 1,000,000 HODL tokens with 18 decimal places
    }

    // Function to mint additional HODL tokens (only the contract owner can call this)
    function mint(address account, uint256 amount) public onlyOwner {
        _mint(account, amount);
    }

    // Function to burn HODL tokens (only the contract owner can call this)
    function burn(address account, uint256 amount) public onlyOwner {
        _burn(account, amount);
    }
}