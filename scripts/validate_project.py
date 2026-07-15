#!/usr/bin/env python3
"""
Validador Completo del Proyecto LeadPilot AI
Verifica estructura, workflow n8n, Airtable schema, prompts y documentación

Uso: python validate_project.py
     python validate_project.py --full
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ValidationStats:
    """Estadísticas de validación"""
    valid: bool = True
    total_files: int = 0
    files_checked: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class LeadPilotAIValidator:
    """Validador completo del proyecto LeadPilot AI"""
    
    REQUIRED_DIRECTORIES = {
        'database': ['airtable_schema.json', 'airtable_schema.csv'],
        'prompts': ['openai_system_prompt.md', 'openai_user_template.md'],
        'tests': ['test_stress_log.txt'],
        'docs': ['ARQUITECTURA.md', 'VARIABLES_DINAMICAS.md', 'SEGURIDAD.md'],
        'evidencias': ['01_diagrama_arquitectura.png', '02_flujo_n8n_evidencia.png', 
                      '03_airtable_schema_evidencia.png', '04_test_estres_evidencia.png',
                      'demo_leadpilot_ai.mp4']
    }
    
    REQUIRED_ROOT_FILES = {
        'README.md',
        'CHECKLIST_ENTREGA.md',
        'leadpilot_ai_n8n_workflow.json',
        '.gitignore',
        '.env.example'
    }
    
    REQUIRED_N8N_NODES = {
        'Gmail Trigger': ['01 Gmail', 'gmail', 'trigger', 'Trigger'],
        'Normalización': ['02 Normalizar', 'normalize', 'variables'],
        'Validación': ['03', 'validar', 'Validar'],
        'Airtable': ['04', 'Airtable', 'airtable'],
        'OpenAI': ['05', 'OpenAI', 'openai', 'IA', 'ia'],
        'IF Score': ['06', '07', 'IF', 'score', 'Score'],
        'Slack HITL': ['Slack', 'slack', 'HITL', 'hitl'],
        'Gmail Output': ['10', 'Gmail', 'email', 'Email'],
        'Error Handling': ['Error', 'error', 'Handling', 'handling']
    }
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.stats = ValidationStats()
        self.n8n_stats = {
            'total_nodes': 0,
            'triggers': 0,
            'ai_nodes': 0,
            'hitl_nodes': 0,
            'connections': 0,
            'components_found': set()
        }
        self.airtable_stats = {
            'tables': 0,
            'fields': 0,
            'relationships': 0
        }
    
    def validate_all(self) -> Tuple[bool, Dict]:
        """Ejecuta validación completa del proyecto"""
        print("\n" + "="*80)
        print("VALIDADOR DE PROYECTO - LeadPilot AI")
        print("="*80)
        
        # 1. Validar estructura de directorios
        self._validate_directories()
        
        # 2. Validar archivos raíz
        self._validate_root_files()
        
        # 3. Validar workflow n8n
        self._validate_n8n_workflow()
        
        # 4. Validar Airtable schema
        self._validate_airtable_schema()
        
        # 5. Validar prompts
        self._validate_prompts()
        
        # 6. Validar .gitignore
        self._validate_gitignore()
        
        # 7. Validar documentación
        self._validate_documentation()
        
        # 8. Validar evidencias
        self._validate_evidences()
        
        return self.stats.valid, self._generate_report()
    
    def _validate_directories(self):
        """Valida estructura de directorios"""
        print("\n🗂️  Validando estructura de directorios...")
        
        for directory, files in self.REQUIRED_DIRECTORIES.items():
            dir_path = self.project_root / directory
            
            if not dir_path.exists():
                self.stats.errors.append(f"Directorio faltante: {directory}/")
                self.stats.valid = False
                continue
            
            for file in files:
                file_path = dir_path / file
                if not file_path.exists():
                    self.stats.errors.append(f"Archivo faltante: {directory}/{file}")
                    self.stats.valid = False
                else:
                    self.stats.files_checked += 1
    
    def _validate_root_files(self):
        """Valida archivos en raíz del proyecto"""
        print("✓ Validando archivos raíz...")
        
        for file in self.REQUIRED_ROOT_FILES:
            file_path = self.project_root / file
            
            if not file_path.exists():
                self.stats.errors.append(f"Archivo raíz faltante: {file}")
                self.stats.valid = False
            else:
                self.stats.files_checked += 1
    
    def _validate_n8n_workflow(self):
        """Valida workflow n8n JSON"""
        print("✓ Validando workflow n8n...")
        
        workflow_path = self.project_root / 'leadpilot_ai_n8n_workflow.json'
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            # Validar estructura
            if 'nodes' not in workflow:
                self.stats.errors.append("Workflow: campo 'nodes' faltante")
                self.stats.valid = False
                return
            
            if 'connections' not in workflow:
                self.stats.errors.append("Workflow: campo 'connections' faltante")
                self.stats.valid = False
                return
            
            # Estadísticas
            self.n8n_stats['total_nodes'] = len(workflow.get('nodes', []))
            node_names = {n.get('name') for n in workflow.get('nodes', [])}
            
            # Buscar componentes clave
            for component, keywords in self.REQUIRED_N8N_NODES.items():
                found = any(
                    any(kw in name for kw in keywords)
                    for name in node_names
                )
                if found:
                    self.n8n_stats['components_found'].add(component)
                else:
                    self.stats.warnings.append(f"Componente n8n no encontrado: {component}")
            
            # Validar conexiones
            self.n8n_stats['connections'] = len(workflow.get('connections', {}))
            
            # Contar tipos de nodos
            for node in workflow.get('nodes', []):
                node_type = node.get('type', '').lower()
                
                if 'gmail' in node_type or 'trigger' in node_type:
                    self.n8n_stats['triggers'] += 1
                
                if 'openai' in node_type:
                    self.n8n_stats['ai_nodes'] += 1
                
                if 'slack' in node_type:
                    self.n8n_stats['hitl_nodes'] += 1
            
            # Validaciones
            if self.n8n_stats['triggers'] == 0:
                self.stats.errors.append("Workflow: No hay trigger (Gmail)")
                self.stats.valid = False
            
            if self.n8n_stats['ai_nodes'] == 0:
                self.stats.errors.append("Workflow: No hay nodo OpenAI")
                self.stats.valid = False
            
            if self.n8n_stats['total_nodes'] < 11:
                self.stats.warnings.append(f"Workflow: Solo {self.n8n_stats['total_nodes']} nodos (esperados: 11+)")
            
        except json.JSONDecodeError as e:
            self.stats.errors.append(f"Workflow JSON inválido: {e}")
            self.stats.valid = False
        except FileNotFoundError:
            self.stats.errors.append("Archivo workflow.json no encontrado")
            self.stats.valid = False
    
    def _validate_airtable_schema(self):
        """Valida Airtable schema JSON"""
        print("✓ Validando Airtable schema...")
        
        schema_path = self.project_root / 'database' / 'airtable_schema.json'
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Extraer tablas (puede estar en raíz o dentro de "tables")
            tables = schema
            if isinstance(schema, dict) and 'tables' in schema:
                tables = schema['tables']
            
            # Validar que sea un array de tablas
            if isinstance(tables, list):
                self.airtable_stats['tables'] = len(tables)
                
                if len(tables) < 3:
                    self.stats.warnings.append(f"Airtable: Solo {len(tables)} tablas (esperadas: 3)")
                
                for table in tables:
                    if 'fields' in table:
                        self.airtable_stats['fields'] += len(table['fields'])
                    
                    if 'relationships' in table:
                        self.airtable_stats['relationships'] += 1
                
                # Validar tablas clave
                table_names = {t.get('name', '') for t in tables}
                required_tables = {'Leads', 'Clientes', 'Errores'}
                missing_tables = required_tables - table_names
                
                if missing_tables:
                    self.stats.warnings.append(f"Airtable: Tablas faltantes: {missing_tables}")
            else:
                self.stats.errors.append("Airtable schema debe contener un array de tablas")
                self.stats.valid = False
        
        except json.JSONDecodeError as e:
            self.stats.errors.append(f"Airtable schema JSON inválido: {e}")
            self.stats.valid = False
        except FileNotFoundError:
            self.stats.errors.append("Airtable schema.json no encontrado")
            self.stats.valid = False
    
    def _validate_prompts(self):
        """Valida prompts OpenAI"""
        print("✓ Validando prompts OpenAI...")
        
        prompt_dir = self.project_root / 'prompts'
        
        for prompt_file in ['openai_system_prompt.md', 'openai_user_template.md']:
            prompt_path = prompt_dir / prompt_file
            
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validaciones básicas
                if len(content) < 100:
                    self.stats.warnings.append(f"Prompt {prompt_file} es muy corto")
                
                # Validar que tenga variables dinámicas
                if prompt_file == 'openai_user_template.md':
                    if '{{' not in content:
                        self.stats.warnings.append(f"Prompt {prompt_file} no tiene variables dinámicas")
            
            except FileNotFoundError:
                self.stats.errors.append(f"Prompt no encontrado: {prompt_file}")
                self.stats.valid = False
    
    def _validate_gitignore(self):
        """Valida .gitignore"""
        print("✓ Validando .gitignore...")
        
        gitignore_path = self.project_root / '.gitignore'
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validaciones de seguridad
            required_ignores = ['.env', '*.key', '*.pem', 'credentials', 'secrets']
            
            for pattern in required_ignores:
                if pattern not in content:
                    self.stats.warnings.append(f".gitignore: Falta patrón de exclusión: {pattern}")
            
            # Validar que permite evidencias
            if '!evidencias/' in content or '!evidencias/*' in content:
                pass  # Bien configurado
            else:
                self.stats.warnings.append(".gitignore: Verificar que permite evidencias/")
        
        except FileNotFoundError:
            self.stats.errors.append(".gitignore no encontrado")
            self.stats.valid = False
    
    def _validate_documentation(self):
        """Valida documentación"""
        print("✓ Validando documentación...")
        
        docs_required = {
            'README.md': ['LeadPilot', 'n8n', 'Airtable'],
            'CHECKLIST_ENTREGA.md': ['requisitos', 'tecnologías'],
            'docs/ARQUITECTURA.md': ['flujo', 'nodos'],
            'docs/SEGURIDAD.md': ['anti-bucles', 'validación'],
            'docs/VARIABLES_DINAMICAS.md': ['variables', 'dinámicas']
        }
        
        for doc_file, keywords in docs_required.items():
            doc_path = self.project_root / doc_file
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # Verificar keywords
                found_keywords = sum(1 for kw in keywords if kw.lower() in content)
                if found_keywords < len(keywords) // 2:
                    self.stats.warnings.append(f"Documentación {doc_file}: Contenido incompleto")
            
            except FileNotFoundError:
                self.stats.errors.append(f"Documentación faltante: {doc_file}")
                self.stats.valid = False
    
    def _validate_evidences(self):
        """Valida archivos de evidencia"""
        print("✓ Validando evidencias...")
        
        evidences_dir = self.project_root / 'evidencias'
        
        expected_files = {
            '01_diagrama_arquitectura.png': 50000,  # Min 50 KB
            '02_flujo_n8n_evidencia.png': 40000,    # Min 40 KB
            '03_airtable_schema_evidencia.png': 30000,  # Min 30 KB
            '04_test_estres_evidencia.png': 30000,  # Min 30 KB
            'demo_leadpilot_ai.mp4': 1000000  # Min 1 MB
        }
        
        for file_name, min_size in expected_files.items():
            file_path = evidences_dir / file_name
            
            if not file_path.exists():
                self.stats.errors.append(f"Evidencia faltante: {file_name}")
                self.stats.valid = False
            else:
                file_size = file_path.stat().st_size
                if file_size < min_size:
                    self.stats.warnings.append(f"Evidencia {file_name}: Tamaño pequeño ({file_size} bytes)")
                else:
                    self.stats.files_checked += 1
    
    def _generate_report(self) -> Dict:
        """Genera reporte final"""
        return {
            'valid': self.stats.valid,
            'project_root': str(self.project_root),
            'files_checked': self.stats.files_checked,
            'n8n_workflow': {
                'total_nodes': self.n8n_stats['total_nodes'],
                'triggers': self.n8n_stats['triggers'],
                'ai_nodes': self.n8n_stats['ai_nodes'],
                'hitl_nodes': self.n8n_stats['hitl_nodes'],
                'connections': self.n8n_stats['connections'],
                'components_found': list(self.n8n_stats['components_found'])
            },
            'airtable_schema': {
                'tables': self.airtable_stats['tables'],
                'fields': self.airtable_stats['fields'],
                'relationships': self.airtable_stats['relationships']
            },
            'errors': self.stats.errors,
            'warnings': self.stats.warnings
        }

def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if not Path(project_root).exists():
        print(f"Error: Directorio no encontrado: {project_root}")
        sys.exit(1)
    
    validator = LeadPilotAIValidator(project_root)
    valid, report = validator.validate_all()
    
    # Mostrar información general
    print(f"\n📁 Proyecto: {report['project_root']}")
    print(f"📊 Archivos verificados: {report['files_checked']}")
    
    # Estadísticas n8n
    n8n = report['n8n_workflow']
    print(f"\n🔧 WORKFLOW n8n:")
    print(f"   • Nodos totales: {n8n['total_nodes']}")
    print(f"   • Triggers: {n8n['triggers']}")
    print(f"   • Nodos IA: {n8n['ai_nodes']}")
    print(f"   • Nodos HITL: {n8n['hitl_nodes']}")
    print(f"   • Conexiones: {n8n['connections']}")
    print(f"   • Componentes encontrados: {len(n8n['components_found'])}/9")
    
    # Estadísticas Airtable
    airtable = report['airtable_schema']
    print(f"\n📊 AIRTABLE:")
    print(f"   • Tablas: {airtable['tables']}")
    print(f"   • Campos totales: {airtable['fields']}")
    print(f"   • Relaciones: {airtable['relationships']}")
    
    # Errores
    if report['errors']:
        print(f"\n❌ ERRORES ({len(report['errors'])}):")
        for error in report['errors']:
            print(f"   • {error}")
    
    # Advertencias
    if report['warnings']:
        print(f"\n⚠️  ADVERTENCIAS ({len(report['warnings'])}):")
        for warning in report['warnings']:
            print(f"   • {warning}")
    
    # Resultado final
    status = "✅ VALIDACIÓN EXITOSA" if valid else "❌ VALIDACIÓN FALLIDA"
    print(f"\n{status}")
    print("="*80 + "\n")
    
    sys.exit(0 if valid else 1)

if __name__ == '__main__':
    main()
