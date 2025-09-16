// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IUniswapV3Pool} from "../interfaces/IUniswapV3Pool.sol";
import {ArbitrumAddresses as ADDR} from "../config/ArbitrumAddresses.sol";

/// @dev ⚠️ Esempio insicuro: usa spot price da slot0, manipolabile; nessuna guard reentrancy.
contract BadVault {
    IUniswapV3Pool public immutable pool; // es: WETH/USDC.e 0.05%
    mapping(address => uint256) public shares;

    constructor() {
        pool = IUniswapV3Pool(ADDR.UNI_V3_POOL_WETH_USDCe_005);
    }

    receive() external payable { deposit(); }

    function deposit() public payable {
        require(msg.value > 0, "no value");
        // SPOT tick manipolabile in 1 tx
        (, int24 tick,,,,,) = pool.slot0();

        // ⚠️ conversione “bogus” (sbagliata, solo didattica)
        uint256 bogusPrice = tick >= 0
            ? uint256(uint24(uint32(uint256(int256(tick)))))
            : 0;

        shares[msg.sender] += msg.value * (bogusPrice + 1);
    }

    function withdraw(uint256 amount) external {
        require(shares[msg.sender] >= amount, "insufficient");
        shares[msg.sender] -= amount;
        // ⚠️ nessun guard contro reentrancy
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "eth send failed");
    }
}
