# optimizer.py
import pulp

def cari_formula_termurah(database_bahan, target_nutrisi):
    prob = pulp.LpProblem("Formulasi_Pakan_Termurah", pulp.LpMinimize)
    
    nama_bahan = list(database_bahan.keys())
    persentase_bahan = pulp.LpVariable.dicts("Persen", nama_bahan, lowBound=0, upBound=100, cat='Continuous')

    # Fungsi Tujuan: Minimalkan total biaya per 100 kg pakan
    prob += pulp.lpSum([database_bahan[i]['harga'] * persentase_bahan[i] for i in nama_bahan]), "Total_Biaya_100kg"

    # Batasan-batasan Nutrisi
    prob += pulp.lpSum([database_bahan[i]['pk'] * persentase_bahan[i] for i in nama_bahan]) >= target_nutrisi["pk_min"] * 100, "Protein_Minimum"
    prob += pulp.lpSum([database_bahan[i]['em'] * persentase_bahan[i] for i in nama_bahan]) >= target_nutrisi["em_min"] * 100, "Energi_Minimum"
    prob += pulp.lpSum([database_bahan[i]['ca'] * persentase_bahan[i] for i in nama_bahan]) >= target_nutrisi["ca_min"] * 100, "Kalsium_Minimum"
    prob += pulp.lpSum([database_bahan[i]['p'] * persentase_bahan[i] for i in nama_bahan]) >= target_nutrisi["p_min"] * 100, "Fosfor_Minimum"
    prob += pulp.lpSum([database_bahan[i]['sk'] * persentase_bahan[i] for i in nama_bahan]) <= target_nutrisi["sk_max"] * 100, "Serat_Maksimal"
    
    # Batasan Total Campuran harus 100%
    prob += pulp.lpSum([persentase_bahan[i] for i in nama_bahan]) == 100, "Total_Persentase"

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[prob.status] == 'Optimal':
        resep = {v.name.replace('Persen_', '').replace('_', ' '): v.varValue for v in prob.variables() if v.varValue > 0.01}
        biaya_per_100kg = pulp.value(prob.objective)
        return resep, biaya_per_100kg / 100, "Optimal"
    else:
        return None, 0, pulp.LpStatus[prob.status]