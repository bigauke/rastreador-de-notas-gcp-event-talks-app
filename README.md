# Rastreador de Notas de Lançamento do BigQuery 🚀

Este é um painel moderno e elegante desenvolvido em **Python Flask**, **Vanilla HTML5**, **CSS3 (com Glassmorphism)** e **JavaScript puro**. Ele foi projetado para monitorar as notas de versão oficiais do Google Cloud BigQuery e permitir o compartilhamento rápido de atualizações relevantes diretamente no Twitter/X.

## 📱 Visualização do Aplicativo
O aplicativo apresenta um design escuro premium com efeitos de desfoque de fundo (Glassmorphism), transições suaves de hover, estados de carregamento animados (Skeleton screens) e total responsividade para dispositivos móveis.

---

## ⚡ Principais Recursos
1. **Histórico de Lançamentos**: Listagem automática de todas as datas de notas de versão oficiais obtidas do feed RSS da Google Cloud.
2. **Separação Inteligente de Atualizações**: O frontend analisa a resposta da API e separa cada seção (ex: `Recurso`, `Alteração`, `Depreciado`, `Removido`) em cartões individuais codificados por cores.
3. **Twitter/X Composer Integrado**:
   - Botão de rascunho rápido em cada cartão para carregar o texto diretamente no compositor.
   - Contador dinâmico de caracteres com limite padrão de 280 caracteres (com indicações visuais de aviso e perigo).
   - Interruptor para incluir ou remover o link de origem das notas de versão.
   - Integração segura por meio do Twitter Web Intent (sem necessidade de chaves de API do Twitter).
4. **Cache Eficiente**: O backend Flask implementa um cache em memória com TTL de 5 minutos para evitar requisições excessivas à API da Google, contendo também um mecanismo de fallback caso a rede falhe.

---

## 🛠️ Tecnologias Utilizadas
* **Backend**: Python 3, Flask.
* **Frontend**: HTML5 Semântico, CSS3 puro (com variáveis nativas e keyframe animations), JavaScript Vanilla (usando `DOMParser` para manipulação segura e análise em tempo real do XML feed).

---

## 🚀 Como Instalar e Executar

### Pré-requisitos
Certifique-se de ter o **Python 3.x** instalado em sua máquina.

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/bigauke/rastreador-de-notas-gcp-event-talks-app.git
cd rastreador-de-notas-gcp-event-talks-app
```

### Passo 2: Instalar as Dependências
Instale o framework Flask usando o gerenciador de pacotes pip:
```bash
pip install flask
```

### Passo 3: Executar a Aplicação
Inicie o servidor de desenvolvimento:
```bash
python app.py
```

### Passo 4: Acessar no Navegador
Abra o navegador e acesse:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Estrutura do Projeto
* `app.py`: Servidor Flask e lógica de cache/parser de RSS feed.
* `templates/index.html`: Interface visual e estrutura do painel.
* `static/style.css`: Design e folha de estilos premium (Glassmorphism).
* `static/script.js`: Parser de tags XML/HTML, contador de caracteres e integração de compartilhamento.
* `.gitignore`: Configuração para ignorar arquivos locais e caches do ambiente Python.
