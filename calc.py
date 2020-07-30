from libs.classes import Cost, Work, Price, Result
from functools import reduce
import sys, copy


cost_list = [
    Cost("CMJ", "0284504024", 1350000),
    Cost("TDSL", "0314496002", 359940),
    Cost("SLI", "0312296004", 200000),
    Cost("昭和大学", "0260867059", 100000),
    Cost("情報発信", "0306311014", 100000),
    Cost("脆弱性診断", "0300469002", 100000), # 2020-08まで
    Cost("J-Power", "0315590001", 88740),
    Cost("支援", "0306311013", 300000),
    Cost("CMJ臨時", "0315855001", 55000),
    Cost("コスト計上", "0217180053", 0),
    ]

work_list = [
    Work("飯渕", 7.5 + 35.5 + 43.5 + 76.5),
    Work("仁野村", 146.5),
    Work("三浦", 153.5 + 1.5),
    Work("越智", 114.25 + 11.5),
    Work("新山", 40 + 0),
    Work("山田", 157.5 + 20 - 7.5),
    ]

ignore_list = [ # They can only use the OVER_COST
    "新山",
    ]

initial_args = [
    ["飯渕", "SLI", 35.5],
    ["飯渕", "TDSL", 43.5],

    ["新山", "情報発信", 20],
    ["新山", "脆弱性診断", 20],

    ["山田", "J-Power", 15],
    ["山田", "CMJ臨時", 7.5 + 1.75],

    ["越智", "昭和大学", 11.5],
    ["越智", "CMJ", 114.25],

    ["三浦", "昭和大学", 1.5],
    ["三浦", "コスト計上", 153.5],
    ]

price_list = [
    Price("山田", 5916),
    Price("越智", 5916),
    Price("飯渕", 4920),
    Price("新山", 4920),
    Price("三浦", 4620),
    Price("仁野村", 4100),
#    Price("米田", 6988),
    ]


def solv(cost_list, work_list, price_list):
    result = []
    work_list = list(filter(lambda x: x.hour > 0, work_list))
    if len(work_list) == 0:
        return result
    name_list = list(map(lambda x: x.name, work_list))
    price_list = list(filter(lambda x:x.name in name_list, price_list))
    minimum_price = reduce(lambda x,y: x if x.price < y.price else y, price_list)
    minimum_work = list(filter(lambda x:x.name == minimum_price.name, work_list))[0]
    max_cost = reduce(lambda x,y: x if x.balance > y.balance else y, cost_list)

    work_hour = minimum_work.hour
    if (minimum_price.price / 4 > max_cost.balance) or (minimum_price.name in ignore_list):
        # cost empty exception or ignore member
        over_cost = list(filter(lambda x:x.name == "コスト計上", cost_list))[0]
        result.append(Result(minimum_work.name, over_cost.name, over_cost.cost_id, work_hour, work_hour*minimum_price.price))
    else:
        if minimum_work.hour * minimum_price.price > max_cost.balance:
            # cost over exception
            work_hour = (max_cost.balance / minimum_price.price) // 0.25 * 0.25
        max_cost.balance -= work_hour * minimum_price.price
        result.append(Result(minimum_work.name, max_cost.name, max_cost.cost_id, work_hour, work_hour*minimum_price.price))
    minimum_work.hour -= work_hour

    result.extend(solv(cost_list, work_list, price_list))

    return result


def initialize(member_name, cost_name, hour):
    price = list(filter(lambda x: x.name == member_name, price_list))[0].price
    cost = list(filter(lambda x: x.name == cost_name, cost_list))[0]
    work = list(filter(lambda x: x.name == member_name, work_list))[0]
    if (cost_name == "コスト計上") or (cost.balance >= hour*price):
        cost.balance -= hour*price
        work.hour -= hour
    else:
        limit = (cost.balance / price) // 0.25 * 0.25
        raise Exception("Cost over Exception: {0} {1} {2}. Reduce in to {3} hours.".format(member_name, cost_name, hour, limit))
    return Result(member_name, cost_name, cost.cost_id, hour, hour*price)


if __name__ == "__main__":
    result = []
    copy_cost_list = copy.deepcopy(cost_list)

    # Minimum value constraint 
    try:
        for name, job, hour in initial_args:
            result.append(initialize(name, job, hour))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    # Calcration    
    result.extend(solv(cost_list, work_list, price_list))

    # Aggregation
    # Select member_name, cost_name, sum(hour), sum(supply) Group by (member_name, cost_name)
    result = sorted(result, key = lambda x: (x.name, x.cost))
    length = len(result)
    if length > 1:
        length -= 1
        while -1 < length :
            if result[length].name == result[length-1].name and result[length].cost == result[length-1].cost:
                result[length-1].set_hour(result[length-1].hour + result[length].hour)
                result[length-1].set_supply(result[length-1].supply + result[length].supply)
                result.pop(length)
            length -= 1

    print("--- output ---")
    [print(r) for r in result]

    print("--- debug ---")
    [print(r.debug()) for r in result]

    print("--- result ---")

    total_balance = sum([c.balance for c in copy_cost_list])
    total_cost = sum([r.supply for r in result if r.cost != "コスト計上"])
    over_cost = sum([r.supply for r in result if r.cost == "コスト計上"])

    # Output the value for each the cost_name
    # Select cost_name, sum(supply) Group by cost_name
    for cost in copy_cost_list:
        estimate = cost.balance
        supply = sum([r.supply for r in result if r.cost == cost.name])
        print("{0}_cost\t {1:09,} - {2:09,} = {3:09,}".format(cost.name, estimate, supply, estimate-supply))

    print("TOTAL_cost\t {0:08,} - {1:08,} = {2:08,}\n".format(total_balance, total_cost, total_balance - total_cost))

    if total_balance >= total_cost:
        print("OK !!")
    else:
        print("Invalid Calcration...")
