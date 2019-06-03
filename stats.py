import ast
import matplotlib.pyplot as plt

rq_f = open('stanfordrq.txt', 'r')
lt_f = open('stanfordlt.txt', 'r')
udp_f = open('stanfordudp.txt', 'r')

rq = rq_f.read()
lt = lt_f.read()
udp = udp_f.read()

rq = ast.literal_eval(rq)
lt = ast.literal_eval(lt)
udp = ast.literal_eval(udp)

rq_f.close()
lt_f.close()
udp_f.close()

# compare at noise level .3 (the 6th element)
rq_3 = rq[6]
lt_3 = lt[6]
udp_3 = udp[6]

print(rq_3)
print(lt_3)
print(udp_3)

# runtime vs noise
rp_runtime = [x[1] for x in rq]
lt_runtime = [x[1] for x in lt]
udp_runtime = [x[1] for x in udp]

plt.plot(list(range(0, 100, 5)), rp_runtime, label = 'raptor')
plt.plot(list(range(0, 100, 5)), lt_runtime, label = 'lt')
plt.plot(list(range(0, 100, 5)), udp_runtime, label = 'udp')
plt.title('Average runtime vs. noise')
plt.xlabel('Percent Noise')
plt.ylabel('Runtime (seconds)')

plt.legend(loc = 'center right')
plt.show()

# print(lt)


# packets required vs noise
rp_runtime = [x[3] for x in rq]
lt_runtime = [x[3] for x in lt]
udp_runtime = [x[3] for x in udp]

plt.plot(list(range(0, 100, 5)), rp_runtime, label = 'raptor')
plt.plot(list(range(0, 100, 5)), lt_runtime, label = 'lt')
plt.plot(list(range(0, 100, 5)), udp_runtime, label = 'udp')
plt.title('Number of received packets vs. noise')
plt.xlabel('Percent Noise')
plt.ylabel('Number of packets received')

plt.legend(loc = 'center right')
plt.show()