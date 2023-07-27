from abstractions.scripts.conf.eval_detector_conf import Config
from abstractions.utils.scripts import run


def main(cfg: Config):
    reference_data = cfg.task.get_reference_data()
    anomalous_data = cfg.task.get_anomalous_data()
    model = cfg.task.get_model()
    params = cfg.task.get_params()
    detector = cfg.detector.build(model=model, params=params, save_dir=cfg.dir.path)

    detector.eval(
        normal_dataset=reference_data,
        anomalous_datasets={"anomalous": anomalous_data},
    )


if __name__ == "__main__":
    run(main, Config, save_config=False)
