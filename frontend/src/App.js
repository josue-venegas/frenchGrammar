import React, { useState, useEffect } from 'react';
import { DndContext, useDroppable } from '@dnd-kit/core';
import { SortableContext, arrayMove, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Button, Alert, Form } from 'react-bootstrap';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronLeft, faChevronRight } from '@fortawesome/free-solid-svg-icons';
import { words } from './initialWords';

const COLORS = {
  "adjectif": "success",
  "adverbe": "info",
  "conjonction": "light",
  "interjection": "secondary",
  "nom": "danger",
  "préposition": "dark",
  "verbe": "warning",
  "pronom": "primary",
  "article": "primary",
  "déterminant": "secondary",
  "négation": "danger",
  "ponctuation": "dark",
}

const TITLES = {
  "adjectif": "Adjetivos",
  "adverbe": "Adverbios",
  "conjonction": "Conjunciones",
  "interjection": "Interjecciones",
  "nom": "Sustantivos",
  "préposition": "Preposiciones",
  "verbe": "Verbos",
  "pronom": "Pronombres",
  "article": "Artículos",
  "déterminant": "Determinantes",
  "négation": "Negaciones",
  "ponctuation": "Puntuación",
}

// Component for the Pill
const Pill = ({ id, text, variant, onRemove, isInstance }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  return (
    <div style={{ display: 'flex', alignItems: 'center', margin: '5px' }}>
      <Button
        ref={setNodeRef}
        {...attributes}
        {...listeners}
        style={{
          transform: CSS.Transform.toString(transform),
          transition,
        }}
        variant={variant in COLORS ? COLORS[variant] : ''}
      >
        {text}
      </Button>
      {isInstance && (
        <Button 
          variant="danger" 
          onClick={() => onRemove(id)} 
          style={{ width: '15px', height: '15px', padding: 0, fontSize: '10px', top: '-10px', position: 'relative' }}
        >
          X
        </Button>
      )}
    </div>
  );
};

// Component for the Pill List
const MainZone = ({ pills, onRemove }) => {
  const { setNodeRef } = useDroppable({ id: 'droppable' });

  return (
    <div ref={setNodeRef} style={{ padding: '10px', border: '1px dashed #ccc', borderRadius: '10px', backgroundColor: '#f2ceaa', minHeight: '200px' }}>
      <h5>Drop zone</h5>
      <small>¡Arrastra las píldoras acá y forma una oración!</small>
      <div style={{ display: 'flex'}}>
        <SortableContext items={pills.map(pill => pill.id)}>
          {pills.map(({ id, text, origin }) => (
            <Pill key={id} id={id} text={text} variant={origin} onRemove={onRemove} isInstance={true} />
          ))}
        </SortableContext>
      </div>
    </div>
  );
};

// CategoryZone Component with Pagination
// Define how many items we want to show per page
const ITEMS_PER_PAGE = 5;
const CategoryZone = ({ id, pills, onRemove }) => {
  const { setNodeRef } = useDroppable({ id });
  const [searchTerm, setSearchTerm] = useState('');
  const [tagsFilter, settagsFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const categories = Array.from(new Set(pills.flatMap(pill => pill.tags)));

  const filteredPills = pills.filter(pill => {
    const matchesSearch = pill.text.toLowerCase().includes(searchTerm.toLowerCase());
    const matchestags = tagsFilter ? pill.tags.includes(tagsFilter) : true;
    return matchesSearch && matchestags;
  });

  const totalPages = Math.ceil(filteredPills.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const pillsToDisplay = filteredPills.slice(startIndex, endIndex);

  const goToPreviousPage = () => setCurrentPage(prevPage => Math.max(prevPage - 1, 1));
  const goToNextPage = () => setCurrentPage(prevPage => Math.min(prevPage + 1, totalPages));

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handletagsChange = (e) => {
    settagsFilter(e.target.value);
    setCurrentPage(1);
  };

  return (
    <div ref={setNodeRef} style={{ padding: '10px', border: '1px solid #000', margin: '10px', minHeight: '150px' }}>
      <h5>{id in TITLES ? TITLES[id] : ''}</h5>
      <Form.Control 
        type="text" 
        placeholder="Buscar palabra..." 
        value={searchTerm} 
        onChange={handleSearchChange} 
        style={{ marginBottom: '10px' }}
      />
      <Form.Select 
        value={tagsFilter} 
        onChange={handletagsChange} 
        style={{ marginBottom: '10px' }}
      >
        <option value="">Filtrar por tipo</option>
        {categories.map(tags => (
          <option key={tags} value={tags}>{tags}</option>
        ))}
      </Form.Select>
      <SortableContext items={pillsToDisplay.map(pill => pill.id)}>
        {pillsToDisplay.map(({ id, text, origin }) => (
          <Pill key={id} id={id} text={text} variant={origin} onRemove={onRemove} />
        ))}
      </SortableContext>
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
          <Button onClick={goToPreviousPage} disabled={currentPage === 1}>
            <FontAwesomeIcon icon={faChevronLeft} />
          </Button>
          <span>{currentPage}/{totalPages}</span>
          <Button onClick={goToNextPage} disabled={currentPage === totalPages}>
            <FontAwesomeIcon icon={faChevronRight} />
          </Button>
        </div>
      )}
    </div>
  );
};

// Main App component
const App = () => {

  // useEffect to load the dictionary once the page is loaded
  const [zones, setZones] = useState({});

  useEffect(() => {
    // Create a dictionary with the initial words
    const initialZones = words.reduce((acc, word) => {
      if (acc[word.origin]) {
        acc[word.origin].push(word);
      } else {
        acc[word.origin] = [word];
      }
      return acc;
    }, {});

    setZones(initialZones);
  }, []);
  
  const [pillsInMainZone, setPillsInMainZone] = useState([]);
  const [alert, setAlert] = useState({ show: false, message: '', variant: '' });

  const handleDragEnd = ({ active, over }) => {
    if (!over) return;

    const targetZone = over.id;

    if (targetZone === 'droppable') {
      // Clonación de la píldora en vez de moverla
      const categoryZone = Object.keys(zones).find(zone => 
        zones[zone].some(pill => pill.id === active.id)
      );

      if (categoryZone) {
        const pill = zones[categoryZone].find(pill => pill.id === active.id);
        const clonedPill = { ...pill, id: `${pill.id}-${Date.now()}`, isInstance: true }; // Genera un nuevo ID único
        setPillsInMainZone(prev => [...prev, clonedPill]);
      }
    } else {
      rearrangePillsInMainZone(active.id, over.id);
    }
  };

  const rearrangePillsInMainZone = (activeId, overId) => {
    const oldIndex = pillsInMainZone.findIndex(pill => pill.id === activeId);
    const newIndex = pillsInMainZone.findIndex(pill => pill.id === overId);

    if (oldIndex !== -1 && newIndex !== -1) {
      const newPills = arrayMove(pillsInMainZone, oldIndex, newIndex);
      setPillsInMainZone(newPills);
    }
  };

  const handleRemovePill = (id) => {
    setPillsInMainZone(prev => prev.filter(pill => pill.id !== id));
  };

  // Helper function to check grammar using an NLP API
  const grammarIsCorrect = async (sentence) => {
    const myKey = ''
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${myKey}`;

    console.log(`Checking grammar for sentence: "${sentence}"`);

    //const prompt = `Dime si la siguiente frase está correcta gramaticalmente. Si es así, responde en el siguiente formato:\n* Resultado: Frase correcta.\n* Significado en Español: <<Frase en Español>>.\nSi no es correcta, responde en el siguiente formato:\n* Resultado: Frase incorrecta.\n* Frase corregida: <<Frase corregida>>.\n* Significado en Español: <<Frase en Español>>.\n* Explicación: <<Pequeña explicación del error cometido>>.\nLa frase a evaluar es: “${sentence}”`;
    const prompt = `Dime si la estructura gramatical de la siguiente oración es correcta en Francés. Si es correcta, responde con "Sí, la gramática es correcta.", la frase recibida y lo que significa en Español. Si no es correcta, responde con "No, la gramática no es correcta.", la frase recibida, cómo debería ser y su signfiicado en Español.\nOración: "${sentence}"\nRespuesta:`;
    const data = {
      "contents": [
        {
          "parts": [
            {
              "text": prompt,
            }
          ]
        }
      ],
      /* "generationConfig": {
        "temperature": 0.1,
        "topP": 0.9,
      } */
    };

    try {
      const response = await axios.post(url, data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Acceder a los datos de la respuesta
      const response_text = response?.data["candidates"][0]["content"]["parts"][0]["text"];
      const isCorrect = (response_text.toLowerCase().includes("la gramática es correcta"));
      
      return { isCorrect: isCorrect, response_text: response_text };

    } catch (error) {
      console.error("Grammar check failed:", error.response ? error.response.data : error.message);
      return { isCorrect: false, response_text: null };
    }

  };

  // Updated handleCheckOrder to use the grammarIsCorrect function
  const handleCheckOrder = async () => {
    // If there are no pills in the main zone, return
    if (pillsInMainZone.length <= 1) {
      return;
    }

    const currentOrder = pillsInMainZone.map(pill => {
      if (pill.origin === 'noun' && pill.tags.includes('proper')) return pill.text;
      else return pill.text.toLowerCase();
    }).join(" ");

    // Remove spaces
    const removeSpaces = currentOrder
    .replace(/' (\w)/g, "'$1")  // Word with apostrophe and next word starting with a letter (e.g. l'homme) 
    .replace(/ ,/g, ",")        // Commas (e.g. salut ,)
    .replace(/ \./g, ".");      // Periods (e.g. salut .)

    // Capitalize first letter if is the first word of the sentence or if it follows a period or exclamation mark
    const formattedWord = removeSpaces
    .replace(/(^|[\.\!]\s+)(\w)/g, (match, p1, p2) => p1 + p2.toUpperCase());

    // Check grammar with NLP
    const { isCorrect, response_text } = await grammarIsCorrect(formattedWord);
  
    if (isCorrect) {
      showAlert(`${response_text}`, "success");
    } else {
      showAlert(
        `${response_text || 'error in suggestion'}`,
        "danger"
      );
    }
  };
  
  const showAlert = (message, variant) => {
    setAlert({ show: true, message, variant });
  };

  const dismissAlert = () => {
    setAlert({ show: false, message: '', variant: '' });
  };

  const handleClear = () => {
    setAlert({ show: false, message: '', variant: '' });
    const updatedZones = Object.keys(zones).reduce((acc, zoneId) => {
      acc[zoneId] = [...zones[zoneId], ...pillsInMainZone.filter(pill => pill.origin === zoneId)];
      return acc;
    }, {});

    setPillsInMainZone([]);
    setZones(updatedZones);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>💬 Aprende Francés con píldoras</h1>
      <DndContext onDragEnd={handleDragEnd}>
        <MainZone pills={pillsInMainZone} onRemove={handleRemovePill} />

        <Button onClick={handleCheckOrder} variant="success" style={{ marginTop: '20px' }}>
          Comprobar gramática
        </Button>
        <Button onClick={handleClear} variant="secondary" style={{ marginTop: '20px', marginLeft: '10px' }}>
          Reiniciar
        </Button>
        {alert.show && (
          <Alert dismissible onClose={dismissAlert} variant={alert.variant} style={{ marginTop: '20px' }}>
            <ReactMarkdown>{alert.message}</ReactMarkdown>
          </Alert>
        )}
        
        <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '20px' }}>
          {Object.keys(zones).map(zoneId => (
            <CategoryZone key={zoneId} id={zoneId} pills={zones[zoneId]} onRemove={handleRemovePill} />
          ))}
        </div>
      </DndContext>

    
    </div>
  );
};

export default App;
