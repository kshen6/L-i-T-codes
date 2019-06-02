# coding: utf-8
from libraptorq import RQEncoder, RQDecoder, RQError


'''
The encode function for RaptorQ codes.

:param opts: List of arguments specifying parameters for RQEncoder or RQDecoder in  the form
       (min_subsymbol_size, symbol_size, max_memory)

:param data: Data to be encoded

:return: Tuple of (data_len, oti_scheme, oti_common, symbols)
'''
def encode(opts, data):
    # Data size must be divisible by RQEncoder.data_size_div
    data_len, n = len(data), RQEncoder.data_size_div
    if data_len % n: data += '\0' * (n - data_len % n)
    
    # Set default values for options
    min_subsymbol_size = 4
    symbol_size= 4
    max_memory= 200

    # If options provided
    if len(opts) > 0:
        min_subsymbol_size, symbol_size, max_memory = opts

    
    with RQEncoder(data, min_subsymbol_size, symbol_size, max_memory) as enc:
        symbols = dict()
        oti_scheme, oti_common = enc.oti_scheme, enc.oti_common
        # print oti_common, oti_scheme

        for block in enc:
            symbols.update(block.encode_iter(repair_rate=0))

        data_encoded = data_len, oti_scheme, oti_common, symbols
    
    # Print original data & encoded data symbols
    # print data
    # print data_encoded[3]

    # Return data length, oti_scheme, oti_common, and symbols,
    # with symbols being the encoded data
    return data_encoded
    


num_fmt = lambda n: '{:,}'.format(n)
class EncDecFailure(Exception): pass

'''
The decode function for RaptorQ codes.

:param data: Tuple containing encoded data – (data_len, oti_scheme, oti_common, symbols)
'''
def decode(data):
    data_len, oti_scheme, oti_common, symbols = data
    # n_syms, n_syms_total, n_sym_bytes = 0, len(symbols), 0

    with RQDecoder(oti_common, oti_scheme) as dec:
        for sym_id, sym in symbols.viewitems(): #dec.add_symbol(sym, sym_id)
            sym_id, sym = int(sym_id), sym
            try: dec.add_symbol(sym, sym_id)
            except RQError as err: continue
            # n_syms, n_sym_bytes = n_syms + 1, n_sym_bytes + len(sym)
            try: data = dec.decode()[:data_len] #dec.decode()[:data['data_bytes']] # strips \0 padding to rq block size
            except RQError as err: pass
            else:
				break
        else:
            return 'Not enough data yet...'
            # raise EncDecFailure(( 'Failed to decode data from {}'
			#     ' total symbols (processed: {}) - {}' ).format(n_syms_total, n_syms, err))
	# print 'Closed RQDecoder' #(%.3fs)...'
	# print 'Decoded', num_fmt(len(data)), 'B of data from', num_fmt(n_syms) ,'processed symbols (,', num_fmt(n_sym_bytes),'B without ids, symbols total:',num_fmt(n_syms_total), ')'
	return data
        # data_decoded = dec.decode()[:data_len]

    # print data_decoded

    # return data_decoded

