import cvxpy as cp 
import numpy as np
import torch


def objective_parameter_matrix(demand_seq, action_0, hit_weight = 1.0, switch_weight = 1.0):
    
    assert action_0.shape[0] == demand_seq.shape[1]
    if demand_seq.shape[1] != 1:
        raise NotImplementedError
    
    
    n = demand_seq.shape[0]
    m = 2*n
    
    switch_sqrt = np.sqrt(switch_weight)
    A = np.zeros([m, n])
    b = np.zeros(m)
    b[0::2] = hit_weight * demand_seq[:,0]
    b[1] = switch_sqrt * action_0[0]
    
    index_pos = (2*np.arange(n), np.arange(n))
    A[index_pos] = hit_weight

    index_pos = (2*np.arange(n)+1, np.arange(n))
    A[index_pos] = switch_sqrt
    index_neg = (2*np.arange(1,n) + 1, np.arange(n-1) )
    A[index_neg] = -switch_sqrt
    
    return A, b

def calculate_offline_optimal(demand_sequence, initial_action, hit_weight = 1.0, switch_weight=1.0):
    
    A, b = objective_parameter_matrix(demand_sequence, initial_action, hit_weight = 1.0, switch_weight = switch_weight)
    
    # Define and solve the CVXPY problem.
    x = cp.Variable(demand_sequence.shape[0])
    cost = cp.sum_squares(A @ x - b)
    prob = cp.Problem(cp.Minimize(cost))
    prob.solve()

    # # Print result.
    # print("\nThe optimal value is", prob.value)
    # print("The optimal x is")
    # print(x.value)
    # print("The norm of the residual is ", cp.norm(A @ x - b, p=2).value)
    
    seq_shape = demand_sequence.shape
    action_optimal = np.zeros(seq_shape[0] + 1)
    action_optimal[0] = initial_action
    action_optimal[1:] = x.value
    
    optimal_cost = prob.value
    
    return action_optimal, optimal_cost



def calculate_offline_optimal_dynamic(demand_sequence, initial_action, hit_weight = 1.0, switch_weight=1.0):
    #action_optimal = []
    optimal_cost = []
    #print(demand_sequence.shape)
    seq_len = demand_sequence.shape[0]
    action_optimal = torch.zeros(demand_sequence.shape[0], demand_sequence.shape[1]+1, demand_sequence.shape[2])
    for i in range(seq_len):
        demand_sequence_in = demand_sequence[i,:,:]
        #print(demand_sequence_in.shape)
        initial_action_in = initial_action[i]
        #print(initial_action_in.shape)
        action_in, optimal_cost_in = calculate_offline_optimal(demand_sequence_in, initial_action_in, hit_weight = 1.0, switch_weight=1.0)
        #action_optimal.append(action_in)
        action_optimal[i,:,:] = torch.from_numpy(action_in).unsqueeze(1)
        optimal_cost.append(optimal_cost_in)
        
        


    
    
    
    optimal_cost = torch.FloatTensor(optimal_cost).unsqueeze(1)
    return action_optimal, optimal_cost
    