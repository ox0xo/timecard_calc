from libs.classes import Cost, Work, Price, Result
from functools import reduce
import sys, copy, yaml, os


with open(os.path.dirname(__file__) + '/badget.yml', encoding="utf8") as file:
    yml = yaml.safe_load(file)
badget_list = [Cost(r["name"], r["id"], r["balance"]) for r in yml["badget"]]

with open(os.path.dirname(__file__) + '/cost.yml', encoding="utf8") as file:
    yml = yaml.safe_load(file)
cost_list = [Price(r["name"], r["price"]) for r in yml["cost"]]

with open(os.path.dirname(__file__) + '/work.yml', encoding="utf8") as file:
    yml = yaml.safe_load(file)
work_list = [Work(r["name"], r["hour"]) for r in yml["work"]]
initial_args = [[r["name"], r["work"], r["hour"]] for r in yml["initial"]]

free_badget = "技術支援"

ignore_list = [ # They can only use the OVER_COST
    # "名前",
    ]

def solv(badget_list, work_list, cost_list):
    result = []
    work_list = list(filter(lambda x: x.hour > 0, work_list))
    if len(work_list) == 0:
        return result
    name_list = list(map(lambda x: x.name, work_list))
    cost_list = list(filter(lambda x:x.name in name_list, cost_list))
    minimum_price = reduce(lambda x,y: x if x.price < y.price else y, cost_list)
    minimum_work = list(filter(lambda x:x.name == minimum_price.name, work_list))[0]
    max_cost = reduce(lambda x,y: x if x.balance > y.balance else y, badget_list)

    work_hour = minimum_work.hour
    if (minimum_price.price / 4 > max_cost.balance) or (minimum_price.name in ignore_list):
        # cost empty exception or ignore member
        over_cost = list(filter(lambda x:x.name == free_badget, badget_list))[0]
        result.append(Result(minimum_work.name, over_cost.name, over_cost.cost_id, work_hour, work_hour*minimum_price.price))
    else:
        if minimum_work.hour * minimum_price.price > max_cost.balance:
            # cost over exception
            work_hour = (max_cost.balance / minimum_price.price) // 0.25 * 0.25
        max_cost.balance -= work_hour * minimum_price.price
        result.append(Result(minimum_work.name, max_cost.name, max_cost.cost_id, work_hour, work_hour*minimum_price.price))
    minimum_work.hour -= work_hour

    result.extend(solv(badget_list, work_list, cost_list))

    return result


def initialize(member_name, cost_name, hour):
    price = list(filter(lambda x: x.name == member_name, cost_list))[0].price
    cost = list(filter(lambda x: x.name == cost_name, badget_list))[0]
    work = list(filter(lambda x: x.name == member_name, work_list))[0]
    if (cost_name == free_badget) or (cost.balance >= hour*price):
        cost.balance -= hour*price
        work.hour -= hour
    else:
        limit = (cost.balance / price) // 0.25 * 0.25
        raise Exception("Cost over Exception: {0} {1} {2}. Reduce in to {3} hours.".format(member_name, cost_name, hour, limit))
    return Result(member_name, cost_name, cost.cost_id, hour, hour*price)


if __name__ == "__main__":
    result = []
    copy_badget_list = copy.deepcopy(badget_list)

    # Minimum value constraint 
    try:
        for name, job, hour in initial_args:
            result.append(initialize(name, job, hour))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    # Calcration    
    result.extend(solv(badget_list, work_list, cost_list))

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

    total_balance = sum([c.balance for c in copy_badget_list])
    total_cost = sum([r.supply for r in result if r.cost != free_badget])
    over_cost = sum([r.supply for r in result if r.cost == free_badget])

    # Output the value for each the cost_name
    # Select cost_name, sum(supply) Group by cost_name
    for cost in copy_badget_list:
        estimate = cost.balance
        supply = sum([r.supply for r in result if r.cost == cost.name])
        print("{0}_cost\t {1:09,} - {2:09,} = {3:09,}".format(cost.name, estimate, supply, estimate-supply))

    print("TOTAL_cost\t {0:08,} - {1:08,} = {2:08,}\n".format(total_balance, total_cost, total_balance - total_cost))

    if total_balance >= total_cost:
        print("OK !!")
    else:
        print("Invalid Calcration...")
