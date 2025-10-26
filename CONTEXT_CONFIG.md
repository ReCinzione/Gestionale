# ⚙️ Context Engineering Configuration

## 🎯 Session Setup Checklist

### 📋 Pre-Development Check
- [ ] Leggere `CONTEXT_REFERENCE.md` per architettura attuale
- [ ] Consultare `CHANGELOG.md` per ultime modifiche
- [ ] Verificare `TODO.md` per priorità correnti
- [ ] Controllare milestone attivo e deadline
- [ ] Identificare dependencies e blockers

### 🔍 Code Analysis Protocol
1. **Understand Current State**
   - Analizzare file coinvolti nella modifica
   - Verificare pattern esistenti e convenzioni
   - Identificare impatti su altri componenti

2. **Plan Implementation**
   - Definire scope preciso della modifica
   - Identificare test cases necessari
   - Pianificare rollback strategy

3. **Execute & Document**
   - Implementare seguendo best practices
   - Aggiornare documentazione rilevante
   - Aggiornare CHANGELOG.md
   - Marcare TODO items completati

## 🏗️ Architecture Quick Reference

### 📁 Key Files to Always Check
```
PRIMARY CONCERNS:
├── main.py                    # Entry point, app config
├── ui/main_window.py          # UI structure, tab management
├── services/ocr_service.py    # OCR/PDF processing logic
├── database/repository.py     # Data access patterns
└── models/*.py                # Data models, validation

SECONDARY CONCERNS:
├── ui/*_tab.py               # Individual tab implementations
├── services/calculator.py     # Business logic
└── database/schema.py         # Database structure
```

### 🔗 Component Dependencies
```
UI Layer:
  ├── main_window.py → all *_tab.py
  ├── *_tab.py → models + repositories + services
  └── Signals: invoice_saved, sale_saved (cross-tab communication)

Data Layer:
  ├── repositories → database connection + models
  ├── models → validation + serialization
  └── schema.py → database structure

Service Layer:
  ├── ocr_service.py → pytesseract + PIL + PyPDF2
  ├── calculator.py → business rules
  └── csv_importer.py → data import/export
```

### 🎨 UI Patterns
```python
# Standard Tab Structure
class SomeTab(QWidget):
    # Signal for cross-component communication
    data_saved = pyqtSignal()
    
    def __init__(self, repo, other_deps):
        super().__init__()
        self.repo = repo
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        # Layout creation
        # Form setup with validation
        # Button connections
        pass
    
    def save_data(self):
        # Validation
        # Repository call
        # UI feedback
        # Signal emission
        self.data_saved.emit()
```

## 🔧 Development Guidelines

### 🎯 Current Focus Areas
**ACTIVE MILESTONE**: OCR Fix (P0)
- PyPDF2 → pdfplumber migration
- EasyOCR implementation
- Image preprocessing improvements

**NEXT MILESTONE**: UI Refresh (P1)
- Material Design implementation
- Theme system
- Responsive layouts

### 🚨 Critical Constraints
- **Backward Compatibility**: Non rompere database esistente
- **User Data**: Preservare tutti i dati utente
- **Dependencies**: Minimizzare nuove dipendenze esterne
- **Performance**: Non degradare performance esistenti

### 📏 Code Standards
```python
# Naming Conventions
class ComponentName:           # PascalCase
    def method_name(self):     # snake_case
        variable_name = ""     # snake_case
        CONSTANT_NAME = ""     # UPPER_SNAKE_CASE

# Error Handling Pattern
try:
    result = risky_operation()
    return result
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    QMessageBox.warning(self, "Error", f"Operation failed: {e}")
    return None
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    QMessageBox.critical(self, "Critical Error", "Unexpected error occurred")
    raise

# UI Feedback Pattern
def long_operation(self):
    self.progress_bar.setVisible(True)
    self.progress_bar.setRange(0, 0)  # Indeterminate
    
    try:
        # Worker thread for heavy operations
        worker = WorkerThread(operation_params)
        worker.finished.connect(self.on_operation_finished)
        worker.error.connect(self.on_operation_error)
        worker.start()
    except Exception as e:
        self.progress_bar.setVisible(False)
        self.handle_error(e)
```

## 📊 Quality Gates

### ✅ Before Committing
- [ ] Code follows existing patterns
- [ ] Error handling implemented
- [ ] UI feedback provided for long operations
- [ ] No hardcoded paths or values
- [ ] Docstrings for public methods
- [ ] TODO.md updated if applicable

### 🧪 Testing Checklist
- [ ] Happy path functionality works
- [ ] Error cases handled gracefully
- [ ] UI remains responsive
- [ ] No data corruption
- [ ] Backward compatibility maintained

### 📝 Documentation Updates
- [ ] CHANGELOG.md entry added
- [ ] CONTEXT_REFERENCE.md updated if architecture changed
- [ ] TODO.md items marked complete
- [ ] Inline code comments for complex logic

## 🔍 Debugging Strategies

### 🐛 Common Issues
1. **OCR Failures**
   - Check Tesseract installation path
   - Verify image preprocessing
   - Test with different image formats
   - Validate regex patterns

2. **Database Errors**
   - Check foreign key constraints
   - Verify data types match schema
   - Test with edge case data
   - Check connection handling

3. **UI Freezing**
   - Move heavy operations to worker threads
   - Add progress feedback
   - Check for infinite loops in event handlers
   - Verify signal/slot connections

### 🔧 Debug Tools
```python
# Temporary debugging code
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug prints
logger.debug(f"Variable state: {variable}")
logger.info(f"Operation completed: {result}")
logger.warning(f"Potential issue: {warning}")
logger.error(f"Error occurred: {error}")

# UI debugging
print(f"Widget geometry: {widget.geometry()}")
print(f"Widget visible: {widget.isVisible()}")
print(f"Widget enabled: {widget.isEnabled()}")
```

## 🎯 Context Prompts

### 🚀 Starting New Feature
```
"Sto implementando [FEATURE_NAME] seguendo l'architettura esistente.
Ho consultato CONTEXT_REFERENCE.md per i pattern.
La feature è priorità [P0/P1/P2/P3] nel TODO.md.
Impatti previsti: [COMPONENTS_AFFECTED].
Need guidance on: [SPECIFIC_QUESTIONS]."
```

### 🐛 Fixing Bug
```
"Sto risolvendo il bug: [BUG_DESCRIPTION].
Componenti coinvolti: [FILES_INVOLVED].
Steps to reproduce: [REPRODUCTION_STEPS].
Expected vs actual behavior: [BEHAVIOR_DIFF].
Proposed solution: [SOLUTION_APPROACH]."
```

### 🔄 Refactoring
```
"Sto refactoring [COMPONENT_NAME] per [REASON].
Current architecture: [CURRENT_STATE].
Target architecture: [TARGET_STATE].
Backward compatibility: [COMPATIBILITY_PLAN].
Testing strategy: [TEST_APPROACH]."
```

## 📚 Knowledge Base

### 🔗 External Resources
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [SQLite Python Tutorial](https://docs.python.org/3/library/sqlite3.html)
- [Tesseract OCR Documentation](https://tesseract-ocr.github.io/)
- [Material Design Guidelines](https://material.io/design)

### 🏆 Best Practices Repository
- **Error Handling**: Always provide user feedback
- **Performance**: Use worker threads for I/O operations
- **UI/UX**: Consistent styling and behavior patterns
- **Data**: Validate input, sanitize output
- **Architecture**: Loose coupling, high cohesion

### 🎨 Design Decisions Log
- **PyQt5 vs PyQt6**: Staying with PyQt5 for stability
- **SQLite vs PostgreSQL**: SQLite sufficient for single-user
- **Tesseract vs Cloud OCR**: Local processing for privacy
- **Monolith vs Microservices**: Monolith appropriate for desktop app

---

## 🔄 Session Workflow

1. **📋 Context Loading** (2 min)
   - Read relevant documentation files
   - Identify current milestone and priorities
   - Check for any blockers or dependencies

2. **🎯 Task Planning** (3 min)
   - Define specific, measurable objectives
   - Identify files that need modification
   - Plan testing approach

3. **💻 Implementation** (Variable)
   - Follow established patterns
   - Implement with proper error handling
   - Add appropriate logging/debugging

4. **✅ Quality Check** (5 min)
   - Test happy path and error cases
   - Verify UI responsiveness
   - Check backward compatibility

5. **📝 Documentation** (3 min)
   - Update CHANGELOG.md
   - Mark TODO items complete
   - Update CONTEXT_REFERENCE.md if needed

**Total Session Overhead**: ~13 minutes
**ROI**: Consistent quality, reduced debugging time, better maintainability