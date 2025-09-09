# backend/tune_hyperparams.py
import optuna
from train_real import RealTrainer

def objective(trial):
    """Optuna ile hyperparameter optimizasyonu"""
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical("batch_size", [4, 8, 16])
    
    trainer = RealTrainer()
    trainer.optimizer = torch.optim.Adam(trainer.model.parameters(), lr=lr)
    # ... eğitim ve validation loss hesapla
    
    return validation_loss

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=20)
print("🎯 Best hyperparameters:", study.best_params)