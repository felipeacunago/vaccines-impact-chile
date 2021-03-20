git clone --filter=blob:none --sparse 'https://github.com/MinCiencia/Datos-COVID19.git'

cd Datos-COVID19
git sparse-checkout add output/producto9/HospitalizadosUCIEtario_T.csv
git sparse-checkout add output/producto9/HospitalizadosUCIEtario.csv
git sparse-checkout add output/producto16/CasosGeneroEtarioEtapaClinica.csv
git sparse-checkout add output/producto16/CasosGeneroEtario.csv
git sparse-checkout add output/producto58/Camas_UCI_diarias_t.csv
git sparse-checkout add output/producto78/total_vacunados_sexo_edad.csv
git sparse-checkout add output/producto10/FallecidosEtario.csv
git sparse-checkout add output/producto10/FallecidosEtario_T.csv