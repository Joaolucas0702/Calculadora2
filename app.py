import streamlit as st
from calculadora import CalculadoraDespesasImoveis
import urllib.parse

st.set_page_config(page_title="Calculadora de Despesas", layout="centered")
st.title("🏠 Calculadora de Despesas")

calculadora = CalculadoraDespesasImoveis()

def converter_para_float(valor_str):
    try:
        return float(valor_str.replace(".", "").replace(",", "."))
    except:
        return 0.0

def formatar_moeda_input(valor_str):
    valor = ''.join(c for c in valor_str if c.isdigit() or c in ",")
    if not valor:
        return "0,00"
    if "," not in valor:
        valor += ",00"
    partes = valor.split(",")
    parte_int = partes[0]
    parte_int = parte_int.lstrip("0") or "0"
    parte_int_formatada = "{:,}".format(int(parte_int)).replace(",", ".")
    return f"{parte_int_formatada},{partes[1][:2].ljust(2,'0')}"

def moeda(valor):
    return f"R\$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def botao_whatsapp(mensagem):
    mensagem_encoded = urllib.parse.quote(mensagem)
    link = f"https://wa.me/?text={mensagem_encoded}"
    html_link = f'<a href="{link}" target="_blank">📲 Compartilhar no WhatsApp</a>'
    st.markdown(html_link, unsafe_allow_html=True)

modo_compra = st.radio("Escolha o tipo de compra do imóvel:", ["Financiado", "À Vista", "Real Fácil"])

if modo_compra in ["Financiado", "À Vista", "Real Fácil"]:
    st.header(f"📄 Dados para {modo_compra}")

    col1, col2 = st.columns(2)

    with col1:
        valor_imovel_str = st.text_input("Valor do Imóvel (R$)", "0,00")
        valor_imovel_str = formatar_moeda_input(valor_imovel_str)
        st.write("↓ " + valor_imovel_str)

        if modo_compra == "Financiado":
            valor_financiado_str = st.text_input("Valor Financiado (R$)", "0,00")
            valor_financiado_str = formatar_moeda_input(valor_financiado_str)
            st.write("↓ " + valor_financiado_str)

            seguro_str = st.text_input("Seguro (verificar na simulação)", "0,00")
            seguro_str = formatar_moeda_input(seguro_str)
            st.write("↓ " + seguro_str)
        else:
            valor_financiado_str = "0,00"
            seguro_str = "0,00"

    with col2:
        cidade = st.selectbox("Cidade", ["Goiânia - GO", "Trindade - GO", "Senador Canedo - GO", "Aparecida de Goiânia - GO"])
        primeiro_imovel = st.checkbox("É o primeiro imóvel?", value=True)

        if cidade == "Aparecida de Goiânia - GO":
            renda_bruta = st.number_input("Renda Bruta (R$)", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        else:
            renda_bruta = 0.0

        if modo_compra == "Financiado":
            tipo_financiamento = st.selectbox("Tipo de Financiamento", ["SBPE", "Minha Casa Minha Vida", "Pro Cotista"])
        else:
            tipo_financiamento = "SBPE" if modo_compra == "À Vista" else "Real Fácil"

    valor_imovel = converter_para_float(valor_imovel_str)
    valor_financiado = converter_para_float(valor_financiado_str)
    seguro = converter_para_float(seguro_str)
    entrada = valor_imovel - valor_financiado

    if st.button("Calcular"):
        try:
            if cidade == "Aparecida de Goiânia - GO":
                resultado = calculadora.calcular_aparecida(
                    valor_imovel, valor_financiado, tipo_financiamento, renda_bruta, seguro, primeiro_imovel
                )
            else:
                resultado = calculadora.calcular_goiania_trindade_canedo(
                    valor_imovel, valor_financiado, tipo_financiamento, cidade, seguro, primeiro_imovel
                )

            if cidade == "Aparecida de Goiânia - GO":
                itbi_entrada = entrada * 0.025
                if renda_bruta <= 4400:
                    aliq = 0.5
                elif renda_bruta <= 8000:
                    aliq = 1
                else:
                    aliq = 1.5
                itbi_fin = valor_financiado * (aliq / 100)
                taxa_exp = 30.00
                itbi_detalhe = f"""
- Sobre o valor da entrada: (2,5% sobre R\$ {moeda(entrada)}) = R\$ {moeda(itbi_entrada)}  
- Sobre o valor financiado: ({aliq}% sobre R\$ {moeda(valor_financiado)}) = {moeda(itbi_fin)}  
- Taxa de Expediente: R\$ {moeda(taxa_exp)}  
- **Total estimado do ITBI:** R\$ {moeda(resultado['ITBI'])}
"""
            elif cidade == "Senador Canedo - GO":
                aliq = 0.005 if valor_financiado <= 500000 else 0.01
                itbi_entrada = entrada * 0.02
                itbi_fin = valor_financiado * aliq
                taxa_exp = 8.50
                itbi_detalhe = f"""
- Entrada: 2% sobre R\$ {moeda(entrada)} = {moeda(itbi_entrada)}  
- Financiado: {aliq*100:.1f}% sobre R\$ {moeda(valor_financiado)} = {moeda(itbi_fin)}  
- Taxa de Expediente: R\$ {moeda(taxa_exp)}  
- **Total estimado do ITBI:** R\$ {moeda(resultado['ITBI'])}
"""
            elif cidade == "Trindade - GO":
                itbi_base = valor_imovel * 0.02
                taxa_exp = 4.50
                itbi_detalhe = f"""
- Valor do imóvel: 2% sobre R\$ {moeda(valor_imovel)} = {moeda(itbi_base)}  
- Taxa de Expediente: R\$ {moeda(taxa_exp)}  
- **Total estimado do ITBI:** R\$ {moeda(resultado['ITBI'])}
"""
            elif cidade == "Goiânia - GO":
                itbi_base = valor_imovel * 0.02
                taxa_exp = 100.00
                itbi_detalhe = f"""
- Valor do imóvel: 2% sobre R\$ {moeda(valor_imovel)} = {moeda(itbi_base)}  
- Taxa de Expediente: R\$ {moeda(taxa_exp)}  
- **Total estimado do ITBI:** R\$ {moeda(resultado['ITBI'])}
"""
            else:
                itbi_detalhe = "Detalhamento não disponível."

            tipo_titulo = {
                "Financiado": "CÁLCULO PARA COMPRA DE IMÓVEL COM FINANCIAMENTO",
                "À Vista": "CÁLCULO PARA COMPRA DE IMÓVEL À VISTA",
                "Real Fácil": "CÁLCULO PARA COMPRA COM PARCELAMENTO INTERNO (REAL FÁCIL)"
            }

            texto = f"""
📟 **{tipo_titulo[modo_compra]}**

🏡 **Informações Gerais**
- **Valor do Imóvel:** {moeda(valor_imovel)}
- **Valor Financiado:** {moeda(valor_financiado)}
- **Entrada:** {moeda(entrada)}
- **Tipo de Financiamento:** {tipo_financiamento}

💰 **Despesas Envolvidas**
1️⃣ **Lavratura de Contrato – {moeda(resultado['Lavratura'])}**
2️⃣ **ITBI – {moeda(resultado['ITBI'])}**

{itbi_detalhe}

3️⃣ **Registro em Cartório – {moeda(resultado['Registro'])}**
✅ **Desconto 50% Aplicado:** {'Sim ✅' if primeiro_imovel else 'Não ❌'}

📦 **Total Estimado:** {moeda(resultado['Total Despesas'])}

⚠️ *Os valores são aproximados e podem variar conforme o cartório e prefeitura local.*
"""

            st.markdown(texto)
            botao_whatsapp(texto)

        except Exception as e:
            st.error(f"Erro ao calcular: {e}")
