"""
Created on Wed Mar 28 10:12:13 2018

@author: Utku Ozbulak - github.com/utkuozbulak
"""
import numpy as np
import torch
from matplotlib import pyplot as plt
from torch.autograd import Variable

from attacks import attack
from misc_functions import (get_params,
                            convert_to_grayscale,
                            save_gradient_images)
from visualization.vanilla_backprop import VanillaBackprop


# from guided_backprop import GuidedBackprop  # To use with guided backprop


def generate_smooth_grad(Backprop, prep_img, target_class, param_n, param_sigma_multiplier):
    """
        Generates smooth gradients of given Backprop type. You can use this with both vanilla
        and guided backprop
    Args:
        Backprop (class): Backprop type
        prep_img (torch Variable): preprocessed image
        target_class (int): target class of imagenet
        param_n (int): Amount of images used to smooth gradient
        param_sigma_multiplier (int): Sigma multiplier when calculating std of noise
    """
    # Generate an empty image/matrix
    smooth_grad = np.zeros(prep_img.size()[1:])

    mean = 0
    sigma = param_sigma_multiplier / (torch.max(prep_img) - torch.min(prep_img)).data[0]
    for x in range(param_n):
        # Generate noise
        noise = Variable(prep_img.data.new(prep_img.size()).normal_(mean, sigma**2))
        # Add noise to the image
        noisy_img = prep_img + noise
        # Calculate gradients
        vanilla_grads = Backprop.generate_gradients(noisy_img, target_class)
        # Add gradients to smooth_grad
        smooth_grad = smooth_grad + vanilla_grads
    # Average it out
    smooth_grad = smooth_grad / param_n
    return smooth_grad

def runsmoothGrad(choose_network = 'AlexNet',
                 target_example = 3,
                 attack_type = 'FGSM'):

#if __name__ == '__main__':
    # Get params
    (original_image, prep_img, target_class, file_name_to_export, pretrained_model) =\
        get_params(target_example,choose_network)

    VBP = VanillaBackprop(pretrained_model)
    # GBP = GuidedBackprop(pretrained_model)  # if you want to use GBP dont forget to
    # change the parametre in generate_smooth_grad

    param_n = 50
    param_sigma_multiplier = 4
    smooth_grad = generate_smooth_grad(VBP,  # ^This parameter
                                       prep_img,
                                       target_class,
                                       param_n,
                                       param_sigma_multiplier)

    # Save colored gradients
    colorgrads = save_gradient_images(smooth_grad, file_name_to_export + '_SmoothGrad_color')
    # Convert to grayscale
    grayscale_smooth_grad = convert_to_grayscale(smooth_grad)
    # Save grayscale gradients
    graygrads = save_gradient_images(grayscale_smooth_grad, file_name_to_export + '_SmoothGrad_gray')
    print('Smooth grad completed')

    fig = plt.figure()
    fig.suptitle(file_name_to_export+' - '+attack_type+' - Smooth BackProp')

    ax1 = fig.add_subplot(2,2,1)
    ax1.imshow(colorgrads)
    ax1.set_title('Smooth BP')
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.imshow(graygrads[:,:,0])
    ax2.set_title('Smooth BP Gray')


    # Now the attack:
    adversarial,advers_class = attack(attack_type,pretrained_model,original_image,file_name_to_export,target_class)
    smooth_grad = generate_smooth_grad(VBP,  # ^This parameter
                                       adversarial,
                                       advers_class,
                                       param_n,
                                       param_sigma_multiplier)

    # Save colored gradients
    colorgrads2 = save_gradient_images(smooth_grad, 'Adversary_'+file_name_to_export + '_SmoothGrad_color')
    # Convert to grayscale
    grayscale_smooth_grad = convert_to_grayscale(smooth_grad)
    # Save grayscale gradients
    graygrads2 = save_gradient_images(grayscale_smooth_grad, 'Adversary_'+file_name_to_export + '_SmoothGrad_gray')
    print('Adversary Smooth grad completed')

    ax3 = fig.add_subplot(2, 2, 3)
    ax3.imshow(colorgrads2)
    ax3.set_title('Adversary Smooth BP')
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.imshow(graygrads2[:,:,0])
    ax4.set_title('Adversary Smooth BP Gray')

    fig.set_size_inches(18.5, 10.5)
    fig.savefig('Concise Results/'+file_name_to_export+'_'+attack_type+'_SmoothGrad',dpi = 100)