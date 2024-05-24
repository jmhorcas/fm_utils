import dd
try:
    import dd.cudd as _bdd
except ImportError:
    import dd.autoref as _bdd
#import dd.autoref as _bdd
from dd import dddmp

def configurations_number(bdd_model: _bdd.BDD) -> int:
    if isinstance(bdd_model, _bdd.Function):
        u_func = bdd_model.root
    elif isinstance(bdd_model, dd.bdd.BDD):
        u_func = next(iter(bdd_model.roots))
    n_vars = len(bdd_model.vars)
    return int(bdd_model.count(u_func, nvars=n_vars))

def main():
    pl_formula = '(Pizza) & (Pizza <=> Topping) & (Pizza <=> Size) & (Pizza <=> Dough) & (CheesyCrust => Pizza) & (Topping <=> (Salami | Ham | Mozzarella)) & ((Normal <=> (!Big & Size)) & (Big <=> (!Normal & Size))) & ((Neapolitan <=> (!Sicilian & Dough)) & (Sicilian <=> (!Neapolitan & Dough))) & (CheesyCrust => Big)'
    variables = ['Pizza', 'Topping', 'Salami', 'Ham', 'Mozzarella', 'Size', 'Normal', 'Big', 'Dough', 'Neapolitan', 'Sicilian', 'CheesyCrust']
    
    # Create the manager
    bdd: _bdd.BDD = _bdd.BDD()
    print(f'Type: {type(bdd)}')
    print(f'BDD (empty) (type: {type(bdd)}): {bdd}')
    # Declare variables
    bdd.declare(*variables)
    # Build the BDD
    root = bdd.add_expr(pl_formula)
    # Print the BDD
    bdd.dump('bdd.png', roots=[root])
    print(f'BDD (original) (type: {type(bdd)}): {bdd}')
    print(f'len: {len(bdd)}')
    print(f'Terminal node (n0): {bdd.false}')
    print(f'Terminal node (n1): {bdd.true}')
    print(f'Vars: {bdd.vars}')
    print(f'Var_levels: {bdd.var_levels}')
    print(f'Root: {root.var}')
    print("==================================================")
    # Reorder variable for optimizing the BDD
    # Print the BDD again to see the diference
    bdd.reorder()
    bdd.dump('bdd_reordered.png', roots=[root])
    print(f'BDD (reordered) (type: {type(bdd)}): {bdd}')
    print(f'len: {len(bdd)}')
    print(f'Terminal node (n0): {bdd.false}')
    print(f'Terminal node (n1): {bdd.true}')
    print(f'Vars: {bdd.vars}')
    print(f'Var_levels: {bdd.var_levels}')
    print(f'Root: {root.var}')
    print("==================================================")
    print(f'Terminal node (n0): {bdd.false}')
    print(f'Terminal node (n1): {bdd.true}')
    print(f'Vars: {bdd.vars}')
    print(f'Var_levels: {bdd.var_levels}')
    print("==================================================")
    print(f'root: {root}')
    print(f'bdd: {root.bdd}')
    print(f'ref: {root.ref}')
    print(f'dag_size: {root.dag_size}')
    print(f'level: {root.level}')
    #print(f'node: {root.node}')  # no use because gives error
    print(f'var: {root.var}')
    print(f'negated: {root.negated}')
    print(f'high: {root.high}')
    print(f'low: {root.low}')
    print(f'support: {root.support}')
    #print(f'manager: {root.manager}')  # no use because gives error
    #n = configurations_number(root)
    #print(f'Configurations: {n}')
    print("==================================================")
    
    from flamapy.metamodels.bdd_metamodel.transformations import DDDMPReader
    bdd = DDDMPReader('Pizzas_uned.dddmp').transform()
    #bdd = dddmp.load('Pizzas_uned.dddmp')
    bdd = bdd.bdd
    print(f'BDD (loaded) (type: {type(bdd)}): {bdd}')
    print(f'Roots: {bdd.roots}')
    root = next(iter(bdd.roots))
    print(f'Terminal node (n0): {bdd.false}')
    print(f'Terminal node (n1): {bdd.true}')
    print(f'Vars: {bdd.vars}')
    print(f'Var_levels: {bdd.var_levels}')
    #print(f'Root: {root.var}')
    print("==================================================")
    print(f'Terminal node (n0): {bdd.false}')
    print(f'Terminal node (n1): {bdd.true}')
    print(f'Vars: {bdd.vars}')
    print(f'Var_levels: {bdd.var_levels}')
    print("==================================================")
    print(f'root: {root}')
    l, low, high = bdd.succ(root)
    print(f'level: {l}')
    print(f'low: {low}')
    print(f'high: {high}')
    l, low, high = bdd.succ(high)
    print(f'level: {l}')
    print(f'low: {low}')
    print(f'high: {high}')
    print(f'len: {len(bdd)}')
    l, low, high = bdd.succ(bdd.false)
    print(f'level terminal: {l}')
    
    #print(f'Root. level_of_var {bdd.var_at_level()}')
    #print(f'ite: {bdd.ite(root, low, high)}')
    #print(f'level, low, high: {bdd.succ(root)}')
    #print(f'bdd: {root.bdd}')
    #print(f'ref: {root.ref}')
    #print(f'dag_size: {root.dag_size}')
    #print(f'level: {root.level}')
    #print(f'node: {root.node}')  # no use because gives error
    #print(f'var: {root.var}')
    #print(f'negated: {root.negated}')
    #print(f'high: {root.high}')
    #print(f'low: {root.low}')
    #print(f'support: {root.support}')
    #level, low, high = bdd.succ(root)
    #u = bdd.find_or_add(level, low, high)
    #u = bdd.ite(root, low, level)
    #print(f'U: {u} {type(u)}')
    #print('level: {level}')
    #print('low: {low}')
    #print('high: {high}')
    print(f'Root: {root}')
    print(f'Levels: {bdd.var_levels}')
    print(f'vars: {bdd.vars}')

    bdd.declare(*bdd.vars)
    bdd2 = _bdd.BDD()
    bdd2.declare(*bdd.vars)
    bdd2.reorder(bdd.var_levels)
    #bdd.copy(root, bdd2)
    #v = bdd.copy(root, bdd2)
    
    n = configurations_number(bdd)
    print(f'Coonfigurations: {n}')
    #bdd.dump('bdd.dddmp', roots=[root], filetype='dddmp')

    #_bdd.copy_bdd(_bdd.Function(root), bdd2)
    #print(f'BDD (wrapped) (type: {type(bdd2)}): {bdd2}')
    #print(f'Levels: {bdd2.var_levels}')
    # print(f'Terminal node (n0): {bdd.false}')
    # print(f'Terminal node (n1): {bdd.true}')
    # print(f'Vars: {bdd.vars}')
    # print(f'Var_levels: {bdd.var_levels}')
    #print(f'Root: {root.var}')

    

if __name__ == '__main__':
   main()


