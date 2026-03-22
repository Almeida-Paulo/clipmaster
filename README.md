# >_ ClipMaster

### Ctrl+C, Ctrl+V com estratégia!

O Clipmaster é um gerenciador de área de transferência (clipboard) moderno, rápido e minimalista para Windows, construído em Python com PyQt6.

Use o aplicativo para gerenciar os itens copiados para a sua área de transferência, colando-os onde quiser, utilizando atalhos personalizados.

![ClipMaster Preview](https://via.placeholder.com/800x450.png?text=Coloque+uma+Screenshot+do+App+Aqui)

## ✨ Funcionalidades

* **Histórico Inteligente:** Salva automaticamente os últimos 10 itens copiados (suporta textos e **imagens**).
* **Colagem Rápida (Hotkeys):** Use `Alt + Shift + 0` ao `9` para colar instantaneamente qualquer item do histórico em qualquer lugar do sistema, sem precisar abrir a interface.
* **Gerenciamento de Sessões (Abas):** Salve o estado atual do seu clipboard em "pastas" (sessões) nomeadas. Ideal para alternar entre diferentes contextos de trabalho, estudos ou pesquisas.
* **Interface Premium:** Design moderno, dark mode nativo, janela frameless (sem bordas padrão do Windows) e navegação fluida.
* **Controle Total:** Copie itens de volta para o clipboard, exclua itens individualmente ou limpe toda a sessão com um clique.

## 🚀 Como Instalar e Executar

### Pré-requisitos
* Python 3.8 ou superior instalado no sistema.
* Sistema Operacional: Windows (devido aos atalhos globais de teclado).

### Instalação

1. Clone este repositório em sua máquina:
```bash
git clone https://github.com/Almeida-Paulo/clipmaster.git
cd clipmaster
```

2. Instale as dependências necessárias:
```bash
pip install PyQt6 keyboard
```

### Execução
Para iniciar o ClipMaster, basta rodar o script principal:
```bash
python ClipMaster.py
```

---

## ⌨️ Como Usar e Atalhos

1. **Copiando:** Copie textos ou imagens normalmente usando `Ctrl + C` ou o botão direito do mouse. O ClipMaster interceptará e salvará no "Clipboard Atual".
2. **Colando:** Vá para o programa onde deseja colar (Word, Navegador, WhatsApp, etc.) e use os atalhos:
   * `Alt + Shift + 0`: Cola o item mais recente.
   * `Alt + Shift + 1`: Cola o penúltimo item.
   * `Alt + Shift + 2` a `9`: Cola os itens anteriores sequencialmente.
3. **Sessões:** Na interface, clique em **"Salvar Sessão"** para guardar os itens atuais. Depois, você pode limpar a tela e, quando precisar, ir no menu **"Sessões Salvas"** para carregar todos aqueles itens de volta para os atalhos.

---

## ⚠️ Solução de Problemas (Troubleshooting)

**Os atalhos (Alt+Shift+...) não estão funcionando?**
A biblioteca `keyboard` do Python precisa de permissões de baixo nível para interceptar e injetar teclas no Windows. Se os atalhos não estiverem respondendo:
1. Feche o ClipMaster.
2. Abra o Prompt de Comando (CMD) ou PowerShell **como Administrador**.
3. Execute o script novamente (`python ClipMaster.py`).

---

## 🛠️ Tecnologias Utilizadas

* **[Python](https://www.python.org/)** - Lógica principal.
* **[PyQt6](https://riverbankcomputing.com/software/pyqt/)** - Interface gráfica de usuário (GUI) moderna e manipulação nativa da área de transferência (QClipboard).
* **[keyboard](https://github.com/boppreh/keyboard)** - Escuta e injeção de atalhos globais no sistema operacional.

---

## 🤝 Contribuindo

Contribuições são sempre bem-vindas! Se você tem alguma ideia para melhorar o ClipMaster:

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/NovaFuncionalidade`)
3. Faça o Commit de suas mudanças (`git commit -m 'Adicionando nova funcionalidade'`)
4. Faça o Push para a Branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

Criado e mantido por **Paulo Almeida**
* GitHub: [@Almeida-Paulo](https://github.com/Almeida-Paulo)