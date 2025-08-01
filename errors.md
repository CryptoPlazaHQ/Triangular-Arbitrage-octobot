PS C:\Users\DELL\Triangular-Arbitrage-octobot> python main.py
Scanning...
Traceback (most recent call last):
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\resolver.py", line 117, in resolve
    resp = await self._resolver.getaddrinfo(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
    )
    ^
aiodns.error.DNSError: (11, 'Could not contact DNS servers')

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\connector.py", line 1532, in _create_direct_connection
    hosts = await self._resolve_host(host, port, traces=traces)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\connector.py", line 1148, in _resolve_host     
    return await asyncio.shield(resolved_host_task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\connector.py", line 1179, in _resolve_host_with_throttle
    addrs = await self._resolver.resolve(host, port, family=self._family)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\resolver.py", line 126, in resolve
    raise OSError(None, msg) from exc
OSError: [Errno None] Could not contact DNS servers

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 208, in fetch
    async with session_method(yarl.URL(url, encoded=True),
               ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              data=encoded_body,
                              ^^^^^^^^^^^^^^^^^^
                              headers=request_headers,
                              ^^^^^^^^^^^^^^^^^^^^^^^^
                              timeout=(self.timeout / 1000),
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              proxy=final_proxy) as response:
                              ^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\client.py", line 1488, in __aenter__
    self._resp: _RetType = await self._coro
                           ^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\client.py", line 770, in _request
    resp = await handler(req)
           ^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\client.py", line 725, in _connect_and_send_request
    conn = await self._connector.connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        req, traces=traces, timeout=real_timeout
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\connector.py", line 642, in connect
    proto = await self._create_connection(req, traces, timeout)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\connector.py", line 1209, in _create_connection    _, proto = await self._create_direct_connection(req, traces, timeout)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\aiohttp\connector.py", line 1538, in _create_direct_connection
    raise ClientConnectorDNSError(req.connection_key, exc) from exc
aiohttp.client_exceptions.ClientConnectorDNSError: Cannot connect to host api.bybit.com:443 ssl:default [Could not contact DNS servers]

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\main.py", line 22, in <module>
    best_opportunities, best_profit = asyncio.run(detector.run_detection(exchange_name))
                                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python313\Lib\asyncio\runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "C:\Python313\Lib\asyncio\runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "C:\Python313\Lib\asyncio\base_events.py", line 725, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\triangular_arbitrage\detector.py", line 112, in run_detection
    last_prices = await get_exchange_last_prices(exchange_name, ignored_symbols or [], whitelisted_symbols)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\triangular_arbitrage\detector.py", line 106, in get_exchange_last_prices 
    tickers, exchange_time = await get_exchange_data(exchange_name)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\triangular_arbitrage\detector.py", line 99, in get_exchange_data
    tickers = await fetch_tickers(exchange)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\triangular_arbitrage\detector.py", line 20, in fetch_tickers
    return await exchange.fetch_tickers() if exchange.has['fetchTickers'] else []
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\bybit.py", line 2375, in fetch_tickers
    await self.load_markets()
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 329, in load_markets
    raise e
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 321, in load_markets
    result = await self.markets_loading
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 288, in load_markets_helper
    markets = await self.fetch_markets(params)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\bybit.py", line 1729, in fetch_markets
    promises = await asyncio.gather(*promisesUnresolved)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\bybit.py", line 1751, in fetch_spot_markets
    response = await self.publicGetV5MarketInstrumentsInfo(self.extend(request, params))
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 940, in request
    return await self.fetch2(path, api, method, params, headers, body, config)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 934, in fetch2
    raise e
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 925, in fetch2
    return await self.fetch(request['url'], request['method'], request['headers'], request['body'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages\ccxt\async_support\base\exchange.py", line 248, in fetch
    raise ExchangeNotAvailable(details) from e
ccxt.base.errors.ExchangeNotAvailable: bybit GET https://api.bybit.com/v5/market/instruments-info?category=spot
bybit requires to release all resources with an explicit call to the .close() coroutine. If you are using the exchange instance with async coroutines, add `await exchange.close()` to your code into a place when you're done with the exchange and don't need the exchange instance anymore (at the end of your async coroutine).
Unclosed client session
}