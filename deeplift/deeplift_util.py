from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
import sys
import os
import numpy as np
from collections import namedtuple
from collections import OrderedDict

def enum(**enums):
    class Enum(object):
        pass
    to_return = Enum;
    for key,val in enums.items():
        if hasattr(val, '__call__'): 
            setattr(to_return, key, staticmethod(val))
        else:
            setattr(to_return,key,val);
    to_return.vals = [x for x in enums.values()];
    to_return.the_dict = enums
    return to_return;


def assert_is_type(instance, the_class, instance_var_name):
    if (not superclass_in_base_classes(
             instance.__class__.__bases__, the_class)):
        raise RuntimeError(instance_var_name+" should be an instance of "
                +the_class.__name__+" but is "+str(instance.__class__)); 
    return True


def superclass_in_base_classes(base_classes, the_class):
    """
        recursively determine if the_class is among or is a superclass of
         one of the classes in base_classes. The comparison is done by
         name so that even if reload is called on a module, this still
         works.
    """
    for base_class in base_classes:
        if base_class.__name__ == the_class.__name__:
            return True 
        else:
            #if the base class in turn has base classes of its own
            if len(base_class.__bases__)!=1 or\
                base_class.__bases__[0].__name__ != 'object':
                #check them. If there's a hit, return True
                if (superclass_in_base_classes(
                    base_classes=base_class.__bases__,
                    the_class=the_class)):
                    return True
    #if 'True' was not returned in the code above, that means we don't
    #have a superclass
    return False


def run_function_in_batches(func,
                            input_data_list,
                            batch_size=10,
                            progress_update=1000):
    #func has a return value such that the first index is the
    #batch. This function will run func in batches on the inputData
    #and will extend the result into one big list.
    assert isinstance(input_data_list, list), "input_data_list must be a list"
    #input_datas is an array of the different input_data modes.
    to_return = [];
    i = 0;
    while i < len(input_data_list[0]):
        if (progress_update is not None):
            if (i%progress_update == 0):
                print("Done",i)
        to_return.extend(func(*[x[i:i+batch_size] for x in input_data_list]));
        i += batch_size;
    return to_return

def mean_normalise_weights_for_sequence_convolution(weights,
                                                    bias,
                                                    weightsHeight=4):
    #weights: outputchannels, inputChannels, windowDims
    assert len(weights.shape)==4
    assert weights.shape[1]==1
    assert weights.shape[2]==weightsHeight
    mean_weights_at_positions=np.mean(weights,axis=2)
    new_bias = bias + np.sum(np.sum(mean_weights_at_positions,axis=2),axis=1)
    mean_weights_at_positions=mean_weights_at_positions[:,:,None,:]
    renormalised_weights=weights-mean_weights_at_positions
    return renormalised_weights, new_bias


def get_mean_normalised_softmax_weights(weights, biases):
    new_weights = weights - np.mean(weights, axis=1)[:,None]
    new_biases = biases - np.mean(biases)
    return new_weights, new_biases
