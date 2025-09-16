// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AggregatorV3Interface} from "../interfaces/IAggregatorV3.sol";

/// @dev Esempio "cosa NON fare": nessun controllo su staleness/decimali.
contract BadPriceConsumer {
    AggregatorV3Interface public feed;
    constructor(address aggregator) { feed = AggregatorV3Interface(aggregator); }

    function latestPriceUnsafe() external view returns (uint256) {
        (, int256 a,,,) = feed.latestRoundData();
        // ⚠️ Nessuna normalizzazione, nessun check sul timestamp: pericoloso
        return uint256(a);
    }
}
