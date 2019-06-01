from libraptorq import RQEncoder
from libraptorq import RQDecoder

data = 'some input string' * 500

# Data size must be divisible by RQEncoder.data_size_div
data_len, n = len(data), RQEncoder.data_size_div
if data_len % n: data += '\0' * (n - data_len % n)

with RQEncoder(data, min_subsymbol_size=4, symbol_size=16, max_memory=200) as enc:

  symbols = dict()
  oti_scheme, oti_common = enc.oti_scheme, enc.oti_common
  print oti_common, oti_scheme

  for block in enc:
    symbols.update(block.encode_iter(repair_rate=0))

data_encoded = data_len, oti_scheme, oti_common, symbols
print data
print data_encoded[3]




data_len, oti_scheme, oti_common, symbols = data_encoded

with RQDecoder(oti_common, oti_scheme) as dec:
  for sym_id, sym in symbols.viewitems(): dec.add_symbol(sym, sym_id)

  data_decoded = dec.decode()[:data_len]

print data_decoded

