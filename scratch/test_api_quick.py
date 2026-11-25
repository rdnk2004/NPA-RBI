import sys, time
sys.path.insert(0, 'src')
from npa_ews import config, data, validation
from npa_ews.models import FixedEffectsRegressor, GnpaXGBModel

print("1. Loading banking panel...", flush=True)
t0 = time.time()
panel = data.load_banking_panel()
ml_df = data.get_model_ready_frame(panel)
print(f"Done in {time.time()-t0:.2f}s", flush=True)

print("2. Fitting FE...", flush=True)
t0 = time.time()
fe = FixedEffectsRegressor()
fe.fit(ml_df)
print(f"Done in {time.time()-t0:.2f}s", flush=True)

print("3. Fitting XGBoost...", flush=True)
t0 = time.time()
train = ml_df[ml_df["year"] <= config.TRAIN_YEAR_MAX]
test = ml_df[ml_df["year"] >= config.TEST_YEAR_MIN]
xgb_model = GnpaXGBModel().fit(train, test)
print(f"Done in {time.time()-t0:.2f}s", flush=True)

print("4. Running walk_forward_cv...", flush=True)
t0 = time.time()
validation_result = validation.walk_forward_cv(ml_df)
print(f"Done in {time.time()-t0:.2f}s", flush=True)

print("5. Running compare_baselines...", flush=True)
t0 = time.time()
baseline_comparison = validation.compare_baselines(ml_df)
print(f"Done in {time.time()-t0:.2f}s", flush=True)

print("6. Loading bank-level panel...", flush=True)
t0 = time.time()
bank_panel = data.load_bank_level_panel()
bank_clean = data.get_bank_level_model_ready(bank_panel)
print(f"Done in {time.time()-t0:.2f}s", flush=True)

print("7. Running validate_bank_level_models...", flush=True)
t0 = time.time()
bank_val = validation.validate_bank_level_models(bank_clean)
print(f"Done in {time.time()-t0:.2f}s", flush=True)

print("All components ran successfully!", flush=True)
