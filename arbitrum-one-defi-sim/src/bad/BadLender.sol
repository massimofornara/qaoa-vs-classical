// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @dev ⚠️ Dimostrazione: "flash loan" naive senza controlli duri sul rimborso.
contract BadLender {
    address public immutable asset = address(0); // ETH native
    mapping(address => bool) public allowed;

    function setAllowed(address a, bool v) external { allowed[a] = v; }

    function flashLoan(uint256 amount, address target, bytes calldata data) external {
        require(allowed[msg.sender], "not allowed");
        uint256 balBefore = address(this).balance;

        // invia ETH e chiama target arbitrario
        (bool ok,) = target.call{value: amount}(data);
        require(ok, "call fail");

        // ⚠️ Controllo post troppo debole, by-passabile
        require(address(this).balance >= balBefore, "oops");
    }

    receive() external payable {}
}
