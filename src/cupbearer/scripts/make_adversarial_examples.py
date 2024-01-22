import os

import matplotlib.pyplot as plt
import torch
import torchattacks
from cupbearer.scripts.conf.make_adversarial_examples_conf import Config
from cupbearer.utils.scripts import run
from loguru import logger
from torch.utils.data import DataLoader, Subset


# TODO: this probably shouldn't be its own script at all, and instead just be
# integrated into the dataset. That would mean significantly less silly passing
# around of arguments.
def main(cfg: Config):
    assert cfg.dir.path is not None  # make type checker happy
    save_path = cfg.dir.path / "adv_examples.pt"
    if os.path.exists(save_path):
        logger.info("Adversarial examples already exist, skipping attack")
        return

    dataset = cfg.data.build()
    if cfg.max_examples:
        dataset = Subset(dataset, range(cfg.max_examples))
    image, _ = dataset[0]
    model = cfg.model.build_model(input_format=image.shape)
    dataloader = DataLoader(
        dataset,
        batch_size=cfg.batch_size,
        shuffle=False,
    )

    atk = torchattacks.PGD(
        model, eps=cfg.eps, alpha=2 / 255, steps=cfg.steps, random_start=True
    )
    rob_acc, l2, elapsed_time = atk.save(dataloader, save_path, return_verbose=True)

    # N.B. rob_acc is in percent while success_threshold is not
    if rob_acc > 100 * cfg.success_threshold:
        raise RuntimeError(
            "Attack failed, new accuracy is"
            f" {rob_acc}% > {100 * cfg.success_threshold}%."
        )

    # Plot a few adversarial examples in a grid and save the plot as a pdf
    adv_examples = torch.load(save_path)["adv_inputs"]
    fig, axs = plt.subplots(3, 3, figsize=(8, 8))
    for i in range(9):
        ax = axs[i // 3, i % 3]
        ax.set_xticks([])
        ax.set_yticks([])
        try:
            ax.imshow(adv_examples[i].permute(1, 2, 0))
        except IndexError:
            pass
    plt.tight_layout()
    plt.savefig(cfg.dir.path / "adv_examples.pdf")


if __name__ == "__main__":
    run(main, Config)
