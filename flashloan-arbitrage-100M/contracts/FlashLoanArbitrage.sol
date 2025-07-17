// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IPool {
    function flashLoanSimple(
        address receiverAddress,
        address asset,
        uint256 amount,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

interface IPoolAddressesProvider {
    function getPool() external view returns (address);
}

interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory);
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract FlashLoanArbitrage {
    address public owner;
    IPoolAddressesProvider public provider;
    IPool public pool;

    address public token = 0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8; // USDC (Arbitrum)
    address public token2 = 0x82af49447d8a07e3bd95bd0d56f35241523fbab1; // WETH
    address public router1 = 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45; // Uniswap v3
    address public router2 = 0x1b02da8cb0d097eb8d57a175b88c7d8b47997506; // SushiSwap

    constructor() {
        owner = msg.sender;
        provider = IPoolAddressesProvider(0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb); // Aave v3 Provider (Arbitrum)
        pool = IPool(provider.getPool());
    }

    function executeFlashLoan(uint256 amount) external {
        require(msg.sender == owner, "Only owner");
        pool.flashLoanSimple(address(this), token, amount, "", 0);
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata
    ) external returns (bool) {
        require(msg.sender == address(pool), "Only Aave pool");
        require(initiator == address(this), "Invalid initiator");

        IERC20(token).approve(router1, amount);
        address ;
        path1[0] = token;
        path1[1] = token2;

        IUniswapV2Router(router1).swapExactTokensForTokens(
            amount,
            1,
            path1,
            address(this),
            block.timestamp
        );

        uint256 token2Balance = IERC20(token2).balanceOf(address(this));
        IERC20(token2).approve(router2, token2Balance);
        address ;
        path2[0] = token2;
        path2[1] = token;

        IUniswapV2Router(router2).swapExactTokensForTokens(
            token2Balance,
            1,
            path2,
            address(this),
            block.timestamp
        );

        uint256 totalDebt = amount + premium;
        IERC20(token).approve(address(pool), totalDebt);

        uint256 profit = IERC20(token).balanceOf(address(this)) - totalDebt;
        if (profit > 0) {
            IERC20(token).transfer(owner, profit);
        }

        return true;
    }

    function withdraw(address _token) external {
        require(msg.sender == owner, "Not owner");
        uint256 bal = IERC20(_token).balanceOf(address(this));
        IERC20(_token).transfer(owner, bal);
    }
}
