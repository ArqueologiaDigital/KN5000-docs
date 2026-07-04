---
layout: page
title: KN7000 Sound Names
permalink: /kn7000-sound-names/
---

# KN7000 Built-in Sound Inventory

The complete list of the KN7000's built-in voice names, extracted from the table
ROM with `table_names.py`. The instrument stores each sound as a variable-length
record (a header plus one 122-byte block per tone-generator layer) containing a
16-character space-padded name field; these names cluster into the tables below.
**1454 names in 11 tables.**

This is a preservation reference — the definitive list of what the instrument can
play. (The multi-language help text and JPEG colour-profile strings that share
the 16-char format are excluded.)


## User / Compile voice banks  
<small>table @ `0x0406dd` — 19 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Compile<br>
Compile Bank 2<br>
User Bank 1<br>
User Bank 2<br>
User Bank 3<br>
Voice Loop<br>
Voice Drum 1<br>
Voice Drum 2<br>
Voice Scat<br>
Whistle Maj<br>
Whistle Min<br>
Piano Minuet<br>
Grandiose<br>
Pizz Ending<br>
Tom Flam 1<br>
Tom Flam 2<br>
Tom Flam 3<br>
Tom Flam 4<br>
12 Bar In Minor<br>
</div>

## Effect & ambience voices  
<small>table @ `0x042d1f` — 23 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Voice Welcome<br>
Church Bells<br>
Birdsong<br>
Waves<br>
Cosmic Maj<br>
Cosmic Min<br>
8 Beat Strum<br>
16 Beat Strum<br>
Pop EP<br>
Pop Synth<br>
Pop Synth Maj<br>
Pop Synth Min<br>
Funk Gtr Strum<br>
Mute Gtr Single<br>
Mute Gtr Strum<br>
Folk Gtr Strum<br>
Folk Guitar Maj<br>
Folk Guitar Min<br>
Rock Piano<br>
Funk 16 Guitar<br>
R&R Guitar<br>
Rock Gtr Strum<br>
R&Roll Sax Maj<br>
</div>

## Latin & loop phrases  
<small>table @ `0x049ec5` — 26 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Samba Loop Low<br>
Samba Loop High<br>
Latin Guitar<br>
Salsa Piano<br>
Salsa Brass Maj<br>
Salsa Brass Min<br>
12/8 Arpeggio<br>
Fifties Vocals<br>
Dreamy Ballad<br>
EP Ballad Maj<br>
EP Ballad Min<br>
4/4 Arpeggio<br>
Angel Ballad<br>
Ballad Backing<br>
Crescendo<br>
Sax Ballad Maj<br>
Sax Ballad Min<br>
Movie Scene<br>
Timpani Roll<br>
Arpeggio 1<br>
Arpeggio 2<br>
Show Piano Maj<br>
Show Piano Min<br>
Jazz Flautist<br>
Big Band Break<br>
Big Band Reeds<br>
</div>

## Jazz & ensemble phrases  
<small>table @ `0x04edcf` — 9 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Jazz Piano<br>
Jazz Gtr Rhythm<br>
Jazz Voices<br>
Jazz Piano Maj<br>
Scat Singer Min<br>
Marching Brass<br>
Polonaise Piano<br>
Folk Clarinet<br>
Bellow Shake<br>
</div>

## Main sound set (pianos, mallets, strings, …)  
<small>table @ `0x090ea0` — 383 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Concert Grand<br>
Piano Mono<br>
Mono Grand<br>
Upright Piano<br>
Bright Piano<br>
Pop Grand<br>
Mellow Piano<br>
Mellow Grand<br>
Baby Grand<br>
Piano 1 Octave<br>
Piano 2 Octave<br>
Rock Piano<br>
Dance Piano<br>
Old Piano<br>
Jangle Piano<br>
Electric Grand<br>
Vintage E.P.1<br>
Vintage E.P.2<br>
Suitcase E.P.<br>
Tremolo E.Piano<br>
Wurly E.Piano<br>
New EP Routes<br>
Hard Tines E.P.<br>
Clava  E.P.<br>
Gentle E.P.<br>
Modulated E.P.<br>
Studio E.P.<br>
EP Wah Wah<br>
Modern E.P.<br>
Modern Suitcase<br>
Crystal E.P.<br>
Shining E.P.<br>
Solid E.P.<br>
Old & New E.P.<br>
Midi Grand 1<br>
Midi Grand 2<br>
Mallet Grand<br>
Groovy Stack<br>
Harpsichord<br>
Spinet Harpsi<br>
Virginal<br>
Harpsi.Octave<br>
Cembalo<br>
Clavi<br>
Strynthed Clav<br>
Soul Clavi<br>
Pulse Clavi<br>
Synth Clavi<br>
Clavi OD<br>
Silly Clavi<br>
Clavi Sin<br>
Glockenspiel<br>
Vibraphone<br>
Jazz Vibes<br>
Straight Vibes<br>
Xylophone<br>
Xylophone Trill<br>
Marimba<br>
Wide Marimba<br>
Marimba Trill<br>
Bottle Marimba<br>
African Mallet<br>
Celesta<br>
Tubular Bells<br>
Clock Bells<br>
Church Bell<br>
Music Box<br>
Toy Piano<br>
Tinkle Bell<br>
Tuned Ensemble<br>
lassical Guitar<br>
icked Nylon Gtr<br>
Soft Nylon Gtr<br>
panish Guitar 1<br>
panish Guitar 2<br>
panish Guitar 3<br>
Touch Flamenco<br>
Jazz Ac.Guitar<br>
ellow Ac.Guitar<br>
Live Nylon Gtr<br>
Plectrum Nylon<br>
Bossa Guitar<br>
c.Gtr.Harmonics<br>
Folk Guitar<br>
Mellow Folk Gtr<br>
ynamic Folk Gtr<br>
Bright Folk Gtr<br>
rilliantFolkGtr<br>
ccompFolkGuitar<br>
ive Folk Guitar<br>
Jazzy Folk Gtr<br>
ashville Ac Gtr<br>
Stereo Strum<br>
Stereo Ac.Gtr<br>
op Steel Ac.Gtr<br>
2 String Guitar<br>
2Str.Gtr & Harm<br>
Nylon El.Ac.Gtr<br>
Steel El.Ac.Gtr<br>
ango's 6 String<br>
Harp Octave<br>
Bright Harp<br>
Jazz Guitar<br>
ive Jazz Guitar<br>
Picked Jazz Gtr<br>
Jazz Strat<br>
Jazz Gtr Octave<br>
Jazz Pop Guitar<br>
right Solid Gtr<br>
ellow Solid Gtr<br>
Clean Solid Gtr<br>
op Solid Guitar<br>
usion Solid Gtr<br>
tudio Solid Gtr<br>
Rhythm Guitar<br>
S.Cont Wah Wah<br>
Rhythm Wah Wah<br>
Wah Wah Lead 1<br>
Wah Wah Lead 2<br>
Mute Guitar<br>
unk Mute Guitar<br>
Stereo Mute Gtr<br>
istortion Gtr 1<br>
istortion Gtr 2<br>
istortion Gtr 3<br>
istortion Gtr 4<br>
Groovy Dt.Gtr 1<br>
Groovy Dt.Gtr 2<br>
unky Distortion<br>
eedback Guitar1<br>
eedback Guitar2<br>
Feedbacker<br>
Lead Guitar<br>
Carnivore Lead<br>
Touch Wah Lead<br>
ock&Roll Guitar<br>
Wheel Wah Wah<br>
Overdrive Gtr 1<br>
Overdrive Gtr 2<br>
Solid Blues 1<br>
Solid Blues 2<br>
Solid Chorus<br>
Rock Harmonics<br>
Country Guitar<br>
Nashville Steel<br>
awaiian Guitar1<br>
awaiian Guitar2<br>
Banjo<br>
Banjo Tremolo<br>
Mandolin<br>
Mandolin Trem.1<br>
Mandolin Trem.2<br>
Bouzouki<br>
Koto<br>
Taisho Koto<br>
aisho Koto Trem<br>
Shamisen<br>
Sitar<br>
Sitar Bend<br>
Kanun<br>
Cumbus<br>
Ukulele<br>
Zither<br>
Dulcimer<br>
Kalimba<br>
Metal Kalimba<br>
Steel Drum<br>
Bonang<br>
Kenong<br>
Sarrons<br>
Slentem<br>
Talking Drum<br>
Timpani<br>
Timpani Tremolo<br>
Sleigh Bell<br>
Agogo<br>
Cowbell<br>
Triangle Open<br>
Triangle Trill<br>
Windchime<br>
Bell Tree<br>
Tambourine<br>
Wood Block<br>
Claves<br>
Castanets<br>
Orch.Bass Drum<br>
Taiko Drum<br>
Melodic Tom<br>
Power Tom<br>
Synth Drum<br>
Analog Tom<br>
Electric Drum<br>
Reverse Cymbal<br>
Reverse Snare<br>
Orchestra Hit<br>
Violin Soloist<br>
Violin<br>
Violin NV<br>
Jazz Violin<br>
Jazz Violin NV<br>
Slow Violin<br>
Slow Violin NV<br>
Country Fiddle<br>
Viola<br>
Viola NV<br>
Cello<br>
Cello NV<br>
Cello Soloist<br>
String Duo<br>
Bowed Bass<br>
Bowed Bass NV<br>
ymphonicStrings<br>
Concert Strings<br>
lassicalStrings<br>
Marcato Strings<br>
Seasons Strings<br>
Violin Ensemble<br>
Viola Ensemble<br>
Cello Ensemble<br>
Bass Ensemble<br>
Slow Strings<br>
Bright Strings<br>
Violin Strings<br>
Chamber Strings<br>
Soft Strings<br>
Octave Strings<br>
Bass Strings<br>
Tremolo Strings<br>
Pizzicato Str.<br>
Synth Strings 1<br>
Synth Strings 2<br>
id Free Strings<br>
Ballad Strings<br>
Choir Aah<br>
Vocal Ah<br>
Pop Vocal Ah<br>
Stereo Vocal Ah<br>
Mixed Choir<br>
Choir Ooh<br>
Vocal Ooh<br>
Chapel Voices<br>
Humming<br>
Synth Vocal<br>
ixed Doo Voices<br>
Girls Doo<br>
Girls Doo Wah<br>
Girls Warm Wah<br>
irls Bright Wah<br>
Girls Doo Bap<br>
Girls DooWahBap<br>
Boys Doo<br>
Boys Ooh<br>
oysFalsetto Ooh<br>
Boys Doo Wah<br>
Boys Wah<br>
Boys Laa<br>
Boys Bap<br>
Boys DooWahBap<br>
oys & Girls Doo<br>
oys & Girls Ooh<br>
B&G Slow Oohs<br>
Chorus Baps<br>
irls & Boys Bap<br>
Jazz Singers<br>
Singing Company<br>
Jazz Singers II<br>
DaDa Octaves<br>
Vocal Doo<br>
Vocal Daa<br>
Bob's Scat<br>
Boy Doo Da<br>
Boy Doo Bap<br>
Boy Doo<br>
Boy Da<br>
Boy Bap<br>
Boy Doo Hum<br>
Sigh Here<br>
Plucked Vocal<br>
Boy Bass<br>
Synth Bap<br>
Chest Hit Perc<br>
oo You Bap Boys<br>
Acapella Basses<br>
La Voix<br>
Doo Lally<br>
Ooh La La<br>
Say Doo Wah<br>
Synthal Cords<br>
Evensong<br>
Perc Organ<br>
Perc Organ DE<br>
Perc Organ NE<br>
azzOrganSoloist<br>
Full Drawbars<br>
ull Drawbars DE<br>
ull Drawbars NE<br>
Jazz Drawbars<br>
azz Drawbars DE<br>
azz Drawbars NE<br>
Accomp Drawbars<br>
ccompDrawbar DE<br>
ccompDrawbar NE<br>
astRotorOrgan 1<br>
astRotorOrgan 2<br>
astRotorOrgan 3<br>
astRotorOrgan 4<br>
Key Click Organ<br>
traight Spinner<br>
60s Movie Organ<br>
Ball Game Organ<br>
Pop Organ<br>
Pop Organ DE<br>
Pop Organ NE<br>
Soul Organ<br>
Soul Organ DE<br>
Soul Organ NE<br>
Rock Organ<br>
Rock Organ DE<br>
Rock Organ NE<br>
Chorale Organ<br>
Gospel Organ<br>
Shaded Organ<br>
Groovy Organ<br>
Organ Harmonics<br>
Techno Organ<br>
60s Organ<br>
Organ Bass<br>
Organ Bass DE<br>
Organ Bass NE<br>
ass Pedals 16+8<br>
Bass Pedals 16'<br>
Euro Tabs Full<br>
right MixedTabs<br>
Euro Tabs 1<br>
Euro Tabs 2<br>
Euro Tabs 3<br>
Euro Tabs 4<br>
Jazz Tabs<br>
USA Tabs<br>
Flowery Jazz<br>
.Theatre Organ1<br>
.Theatre Organ2<br>
Far Fee Sir<br>
Chapel Organ<br>
Full Organ<br>
Cathedral Organ<br>
Theatre Organ<br>
Theatre Novelty<br>
Seaside Organ<br>
Tibia Chorus<br>
Harmonium<br>
Puff Organ<br>
Full Theatre 1<br>
Full Theatre 2<br>
Full Theatre 3<br>
Full Theatre 4<br>
heatre Romance1<br>
heatre Romance2<br>
heatre Sizzle 1<br>
heatre Sizzle 2<br>
ollow Theatre 1<br>
ollow Theatre 2<br>
heatre Accomp 1<br>
heatre Accomp 2<br>
heatre Accomp 3<br>
heatre Accomp 4<br>
Theatre Sparkle<br>
hrysoglotAccomp<br>
Tibia Pedals<br>
Open Tibias<br>
Flute Chorus<br>
Theatre Vox<br>
Echo Reeds<br>
8 Foot Mixture<br>
Majestic Organ<br>
T.O.Brass&Reeds<br>
Mixed Ranks<br>
Glam Musette<br>
Musette<br>
Wide Musette<br>
Cajun Accordion<br>
Bandoneon<br>
Folk Accordion<br>
</div>

## Accordion registers  
<small>table @ `0x0b4264` — 33 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
German Acdn 1<br>
German Acdn 2<br>
German Acdn 3<br>
German Acdn 4<br>
German Acdn 5<br>
German Acdn 6<br>
German Acdn 7<br>
German Acdn 8<br>
German Acdn Bs1<br>
German Acdn Bs2<br>
Italian Acdn 1<br>
Italian Acdn 2<br>
Italian Acdn 3<br>
Italian Acdn 4<br>
Italian Acdn 5<br>
Italian Acdn 6<br>
Italian Acdn 7<br>
Italian Acdn 8<br>
French Acdn 1<br>
French Acdn 2<br>
French Acdn 3<br>
French Acdn 4<br>
French Acdn 5<br>
French Acdn 6<br>
French Acdn 7<br>
French Acdn 8<br>
French Acdn Bs1<br>
French Acdn Bs2<br>
French Acdn 9<br>
French Acdn 10<br>
French Acdn 11<br>
French Musette1<br>
French Musette2<br>
</div>

## Sound set 2 (accordion, brass, reeds, …)  
<small>table @ `0x0b7a3a` — 430 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Supermusette<br>
Trumpet Soloist<br>
Trumpet<br>
Trumpet NV<br>
Solo Trumpet<br>
Solo Trumpet NV<br>
Trumpet Shake<br>
azz Tpt Soloist<br>
Breathy Trumpet<br>
Soft Trumpet<br>
Soft Trumpet NV<br>
Orchest.Trumpet<br>
Trumpet Fall<br>
Trumpet Up<br>
Up/Down Trumpet<br>
Harmon Mute Tpt<br>
armonMuteTpt NV<br>
StraightMuteTpt<br>
traightMuteTpNV<br>
Cornet Soloist<br>
Cornet<br>
Cornet NV<br>
Flugel Horn<br>
Flugel Horn NV<br>
Flugel Soloist<br>
Bright Trombone<br>
rightTromboneNV<br>
Mellow Trombone<br>
ellowTromboneNV<br>
rombone Soloist<br>
Trombone Shake<br>
azz Tbn Soloist<br>
Jazz Trombone<br>
azz Trombone NV<br>
romboneShrtFall<br>
romboneLongFall<br>
Slide Trombone<br>
Trombone Up<br>
ong & The Short<br>
CupMuteTrombone<br>
upMuteTrombonNV<br>
ute Tbn Soloist<br>
Closed Fr.Horn<br>
Open Fr.Horn<br>
French Horns<br>
Marching Tuba<br>
Orchestral Tuba<br>
Bariton Horn<br>
Bariton Parp<br>
Bigband Brass<br>
Full Brass<br>
Brass Band<br>
ow Unison Horns<br>
Real Brass Pad<br>
Octave Brass<br>
Octave Horns<br>
Horn Section<br>
Pop Trumpets<br>
op Trumpets Oct<br>
rumpet Ensemble<br>
Shake It Up<br>
Brass & Sax<br>
Bavarian Brass<br>
Sfz Brass Oct.<br>
Brass Fall<br>
Brass Falls<br>
Unison Slides<br>
Up/Down Brass<br>
Mute Ensemble 1<br>
Mute Ensemble 2<br>
Muted Horn<br>
Brass & Synth<br>
nalog Syn.Brass<br>
Fat Synth Brass<br>
Basic Syn.Brass<br>
arm Synth Brass<br>
Pop Synth Brass<br>
Block Synth<br>
Brassy Synth<br>
Mecury Pad<br>
Wet Synth Brass<br>
Synth Brass Mix<br>
ynth Brass Band<br>
SynthBrassPad 1<br>
SynthBrassPad 2<br>
Soprano Sax<br>
Soprano Sax NV<br>
Sop Sax Soloist<br>
lto Sax Soloist<br>
oft AltoSoloist<br>
Alto Sax<br>
Alto Sax NV<br>
Jazz Alto Sax<br>
azz Alto Sax NV<br>
Mellow Alto Sax<br>
Mellow Alto NV<br>
Rock Alto Sax<br>
Funky Alto Sax<br>
Growl Alto Sax<br>
enorSax Soloist<br>
Tenor Sax<br>
Tenor Sax NV<br>
Breathy Tenor<br>
reathy Tenor NV<br>
Rock Tenor Sax<br>
Funky Tenor Sax<br>
Growl Tenor Sax<br>
Baritone Sax<br>
Baritone Sax NV<br>
ari.Sax Soloist<br>
anceBandUnison2<br>
Big Band Reeds<br>
Unison Reeds<br>
Distortion Sax<br>
Unison Saxes<br>
Octave Saxes<br>
Jazz Clarinet 1<br>
azzClarinet1 NV<br>
larinet Soloist<br>
Jazz Clarinet 2<br>
azzClarinet2 NV<br>
azzClariSoloist<br>
omanticClarinet<br>
omanticClarntNV<br>
Mellow Clarinet<br>
ellowClarinetNV<br>
lassic Clarinet<br>
Bass Clarinet<br>
anceBandUnison1<br>
Oboe NV<br>
Oboe Soloist<br>
Double Reeds 1<br>
English Horn<br>
English Horn NV<br>
rchestral Woods<br>
Bassoon<br>
Bassoon NV<br>
Bassoon Soloist<br>
Double Reeds 2<br>
Harmonica<br>
Harmonica NV<br>
armonicaSoloist<br>
allad Harmonica<br>
Blues Harmonica<br>
Blues Harm. NV<br>
Bagpipe<br>
Shanai<br>
Piccolo<br>
Piccolo NV<br>
Flute Soloist<br>
azzFluteSoloist<br>
Jazz Flute<br>
Jazz Flute NV<br>
Classical Flute<br>
lassic Flute NV<br>
Chiff Flute<br>
Chiff Flute NV<br>
hifFluteSoloist<br>
Alto Flute<br>
Alto Flute NV<br>
Alto Ensemble<br>
Flutter Flute<br>
lutterFlSoloist<br>
Flugel Flute<br>
anFlute Soloist<br>
Pan Flute 1<br>
Pan Flute 1 NV<br>
Pan Flute 2<br>
Pan Flute 2 NV<br>
Penny Whistle<br>
enny Whistle NV<br>
Low Whistle<br>
Low Whistle NV<br>
Recorder<br>
Recorder NV<br>
ecorder Soloist<br>
Ocarina<br>
Ocarina NV<br>
Blown Bottle<br>
Whistle<br>
Whistle NV<br>
arching Whistle<br>
Siny Whistle<br>
Shakuhachi<br>
Shakuhachi NV<br>
Quena<br>
Acoustic Bass<br>
Mellow Ac.Bass<br>
Wild Ac.Bass<br>
Electric Bass<br>
Mellow E.Bass<br>
Jazz E.Bass<br>
Bright E.Bass<br>
Fusion E.Bass<br>
Funky E.Bass<br>
Touch Funk Bass<br>
Fretless Bass<br>
Picked E.Bass<br>
Mute Bass<br>
Slap Bass 1<br>
Slap Bass 1 v<br>
Slap Bass 2<br>
Slap Bass 2 v<br>
arty March Bass<br>
Analog Bass<br>
House Bass<br>
Dance Bass<br>
asic Synth Bass<br>
Soul Bass<br>
Plastic Bass<br>
Wow Bass<br>
ure Analog Bass<br>
Thick Ana.Bass<br>
ide Analog Bass<br>
Mini Bass<br>
Midland Bass<br>
Techno Bass<br>
Bass Leader<br>
ocky Synth Bass<br>
Rubber Bass<br>
Killer Bass<br>
Fat Tri Bass<br>
Sub Bass<br>
Garage Bass<br>
Garage Bass Too<br>
Jungle Bass<br>
intage Syn.Bass<br>
ard Techno Bass<br>
Tech Step Bass<br>
Wet Bass<br>
70s Square Bass<br>
Frog Bass<br>
Bass Slide<br>
Strings & Horns<br>
Finalegrande<br>
trings & Flutes<br>
trings & Voices<br>
eavenly Strings<br>
Warm String Pad<br>
Chamber Orch<br>
Cathedral<br>
Movie Musical<br>
Horns & Woods<br>
ark Movie Scene<br>
rchestral Sweep<br>
Moonlight Pad<br>
Orchestra Pizz<br>
Synth Orchestra<br>
Cinematic Drama<br>
Unison Strings<br>
Springtime Orch<br>
ractically Huge<br>
Dreamy Strings<br>
Ooh Strings<br>
Aah Strings<br>
Many Horns<br>
Big Band Pad<br>
12 String Pad<br>
Pad Guitar<br>
Piano & Strings<br>
G.Piano&Strings<br>
Piano Orchestra<br>
Symphonic Piano<br>
Piano Cosmos<br>
Dream Piano<br>
Funky Pad<br>
FM Piano Pad<br>
Pop E.P.Pad<br>
Mellow Tines<br>
Pad Grand<br>
Pad Grand Funk<br>
New Age<br>
Big Midi Layer<br>
6 String Piano<br>
Mod.Jazz Piano<br>
Fantasia<br>
Dream<br>
Bell Pad<br>
Bell Line<br>
Light Celestpad<br>
Snowfall Pad<br>
Mellow Ensemble<br>
Poly Synth Pad<br>
Paddy Pad Pad<br>
Ooh Pad<br>
Synth Vocal Pad<br>
Warm Voice Pad<br>
Field of Voices<br>
Softy Pad<br>
Soft Saws<br>
Warm Synth Pad<br>
Slow Synth Pad<br>
Warm Pad Basics<br>
Mixed Osc Pad<br>
Comodore<br>
igh Dyn Alg Pad<br>
Oldie Pad<br>
Spacy Pad<br>
Planet Pad<br>
Itopia<br>
Bowed Glass<br>
Sine Pad<br>
Pure Sinus Pad<br>
Metal Pad<br>
PWM Pad<br>
Halo Pad<br>
Sweep Pad<br>
Multi Sweeper<br>
Voice Sweeper<br>
Warm Sweeper<br>
Atmosphere<br>
Mist<br>
Release Pad<br>
Star Theme<br>
TVF Brass Pad<br>
Hugestring Pad<br>
Trem String Pad<br>
Good Old Waves<br>
Square Lead<br>
Mini Solo<br>
Basic Square<br>
Basic Pulse<br>
The Basics<br>
Too Square<br>
Sub Defusion<br>
Square Bell<br>
Dead Ringer<br>
Sine Lead<br>
Percsine<br>
Soft Lead<br>
Basic Sine<br>
Spleeny Synth<br>
Saw Lead<br>
Boy's Saw Lead<br>
Basic Sawtooth<br>
Blunt Saw<br>
Basic Triangle<br>
Chain Saw<br>
Boy's Doubl Saw<br>
Basic Leader<br>
Fat Leader<br>
Mono Screech<br>
Parp Parp<br>
Weeeow<br>
Wheel Weeeow<br>
Sweep Ana.Synth<br>
awtooth Control<br>
Noiz Boyz<br>
emused Triangle<br>
Frog March<br>
Poly Synth<br>
80s Poly Synth<br>
Big Saw<br>
Maverik<br>
Southlead<br>
Olymp Synth<br>
Synth Calliope<br>
Talking Flute<br>
Chiffer Lead<br>
First Book Lead<br>
Talking Synth<br>
Talking Lead<br>
Voco Synth<br>
Chopper Flute<br>
Charang<br>
Wire Lead<br>
Funky Buzz<br>
Turky Lead<br>
Sweepy Lead<br>
Cat Guitar<br>
Solo Synth<br>
Air Vox<br>
Steamy Keys<br>
5th Wave<br>
Electro Synth<br>
80s Solo<br>
Tune Me In<br>
Bass & Lead<br>
Bass To Lead<br>
Freezy B.& Lead<br>
Metallic Solo<br>
80s Solo Man<br>
Percy Synth<br>
Pick Your Pad<br>
Git'Dreams<br>
Bouncing Creak<br>
Digi Stack<br>
70s Shine<br>
Siren@space<br>
Old Sampler<br>
Rave Chord<br>
70s Fat Synth<br>
HPF Pulser<br>
Crystal<br>
Digi Bells<br>
Space Glocken<br>
Synth Mallet<br>
FM Dreams<br>
Sine Drops<br>
Sequence Dance<br>
Cheap Synth<br>
SEQ Synthy 1<br>
SEQ Synthy 2<br>
SEQ Synthy 3<br>
SEQ Synthy 4<br>
SEQ Techno<br>
Sine Harp<br>
Synth Harp<br>
Synth Lute<br>
Afro Dance<br>
Sine Stab<br>
Breath Perc<br>
Dance Hit<br>
Hip Hop Perc<br>
Ice Rain<br>
5ths Wobble<br>
Soundtrack<br>
Hit Wah<br>
Goblins<br>
Fizzy Nessie<br>
I'm Dreaming...<br>
Nightfly<br>
Echo Drops<br>
Echo Bell<br>
Echo Pan<br>
Tape Reverse<br>
Filter Mayhem<br>
The Spins<br>
Sawn Off Synth<br>
Sirens<br>
</div>

## Sound set 3 (guitar articulations, effect samples, …)  
<small>table @ `0x0de11e` — 374 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Double Cutting<br>
Mute Wah Wah<br>
A.Gtr Body Hit<br>
A.Gtr Fret Hit<br>
Flute Key Click<br>
Breath Noise<br>
Seashore<br>
Thunder<br>
Stream<br>
Bubble<br>
Bird Tweet<br>
Horse Gallop<br>
Telephone 1<br>
Telephone 2<br>
Door Creaking<br>
Scratch<br>
Helicopter<br>
Car Engine<br>
Car Stop<br>
Car Pass<br>
Car Crash<br>
Siren<br>
Train<br>
Jetplane<br>
Starship<br>
Burst Noise<br>
Applause<br>
Laughing<br>
Scream<br>
Punch<br>
Heart Beat<br>
Footsteps<br>
Tap Dancer<br>
Gun Shot<br>
Machine Gun<br>
Laser Gun<br>
Explosion<br>
Standard Kit1<br>
Standard Kit2<br>
LiveStandardKit<br>
Live Rock Kit<br>
Pop Kit<br>
Room Kit<br>
Live Room Kit<br>
Light Rock Kit<br>
Power Kit<br>
Funk Kit<br>
Live Funk Kit<br>
Electric Kit<br>
Trad Kit<br>
Jazz Kit<br>
Live Jazz Kit 1<br>
Live Jazz Kit 2<br>
Brush Kit<br>
Analog Kit 1<br>
Analog Kit 2<br>
Soul Kit<br>
Dance Kit 1<br>
Dance Kit 2<br>
House Kit<br>
Techno Kit<br>
Hip Hop Kit<br>
Bongo&Conga Kit<br>
Orchestral Kit<br>
Voice Kit<br>
<Jazz Drawbars><br>
<Rock Drawbars><br>
<  USA Tabs   ><br>
<European Tabs><br>
<Theatre Pipes><br>
Grand Piano *<br>
Bright Piano *<br>
Honky-Tonk  *<br>
Vintage E.P.*<br>
Modern E.P.*<br>
Harpsichord *<br>
Clavi *<br>
Celesta *<br>
Glockenspiel *<br>
Music Box *<br>
Vibraphone *<br>
Marimba *<br>
Xylophone *<br>
Tubular Bells *<br>
Dulcimer *<br>
Drawbar Organ *<br>
Perc Organ *<br>
Rock Organ *<br>
Church Organ *<br>
Reed Organ *<br>
Accordion *<br>
Harmonica *<br>
Bandoneon *<br>
Nylon Str.Gtr *<br>
Steel Str.Gtr *<br>
Jazz Guitar *<br>
Clean Guitar *<br>
Mute Guitar *<br>
Overdrive Gtr *<br>
istortion Gtr *<br>
Gtr Harmonics *<br>
Acoustic Bass *<br>
ingered E.Bass*<br>
Picked E.Bass *<br>
Fretless Bass *<br>
Slap Bass 1 *<br>
Slap Bass 2 *<br>
Synth Bass 1 *<br>
Synth Bass 2 *<br>
Violin *<br>
Viola *<br>
Cello *<br>
Contrabass *<br>
Tremolo Str *<br>
Pizzicato Str.*<br>
Timpani *<br>
Strings *<br>
Slow Strings *<br>
ynth Strings 1*<br>
ynth Strings 2*<br>
Choir Aahs *<br>
Vocal Doo *<br>
Synth Vocal *<br>
Orchestra Hit *<br>
Trumpet *<br>
Trombone *<br>
Mute Trumpet *<br>
French Horn *<br>
Brass *<br>
Synth Brass 1 *<br>
Synth Brass 2 *<br>
Soprano Sax *<br>
Alto Sax *<br>
Tenor Sax *<br>
Baritone Sax *<br>
English Horn *<br>
Bassoon *<br>
Clarinet *<br>
Piccolo *<br>
Flute *<br>
Recorder *<br>
Pan Flute *<br>
Blown Bottle *<br>
Shakuhachi *<br>
Whistle *<br>
Ocarina *<br>
Square Lead *<br>
Saw Lead *<br>
Syn Calliope *<br>
Chiffer Lead *<br>
Charang *<br>
Solo Vox *<br>
5th Saw Wave *<br>
Bass & Lead *<br>
Fantasia *<br>
Warm Pad *<br>
Poly Synth *<br>
Spacy Vox *<br>
Bowed Glass *<br>
Metal Pad *<br>
Halo Pad *<br>
Sweep Pad *<br>
Ice Rain *<br>
Soundtrack *<br>
Crystal *<br>
Atmosphere *<br>
Brightness *<br>
Goblins *<br>
Echo Drops *<br>
Star Theme *<br>
Sitar *<br>
Banjo *<br>
Shamisen *<br>
Kalimba *<br>
Bagpipe *<br>
Fiddle *<br>
Shanai *<br>
Tinkle Bell *<br>
Agogo *<br>
Steel Drum *<br>
Wood Block *<br>
Taiko Drum *<br>
Melodic Tom *<br>
Synth Drum *<br>
Fret Noise *<br>
Breath Noise *<br>
Seashore *<br>
Bird Tweet *<br>
Telephone *<br>
Helicopter *<br>
Applause *<br>
Gun Shot *<br>
Grand Piano w *<br>
Mellow Piano *<br>
E.Grand w *<br>
Honky-Tonk w *<br>
Honky-Tonk 2<br>
Vintage E.P.v *<br>
60s E.Piano *<br>
Vintage E.P.3<br>
Suitcase E.P.2<br>
Modern E.P.v *<br>
EP Legend *<br>
EP Phase *<br>
Modern E.P.2<br>
Harpsi.Octave *<br>
Harpsichord w *<br>
Harpsichord 2 *<br>
Harpsichord 2<br>
Harpsichord 3<br>
Pulse Clavi *<br>
Vibraphone w *<br>
Vibraphone 2<br>
Marimba w *<br>
Marimba 2<br>
Church Bell *<br>
Carillon *<br>
Cho.Drawbars *<br>
60s Organ *<br>
rawbar Organ 2*<br>
Drawbar Organ 2<br>
Drawbar Organ 3<br>
Drawbar Organ 4<br>
ho.Perc Organ *<br>
Perc Organ 2 *<br>
Perc Organ 2<br>
Perc Organ 3<br>
Church Organ 2<br>
Church Organ 3<br>
Puff Organ *<br>
Accordion 2 *<br>
Ukulele *<br>
ylon Str.Gtr 2*<br>
ylon Str.Gtr 3*<br>
Ukulele 2<br>
Jazz Ac.Gtr 2<br>
Jazz Ac.Gtr 3<br>
12 String Gtr *<br>
Mandolin *<br>
teel Str.Gtr 2*<br>
12 String Gtr 2<br>
Mandolin 2<br>
edal Steel Gtr*<br>
edal Steel Gtr2<br>
Chorus Guitar *<br>
lean Guitar 2 *<br>
Chorus Guitar<br>
Funk Guitar *<br>
Mute Guitar 2 *<br>
Jazz Man *<br>
Funk Guitar 1<br>
Funk Guitar 2<br>
Guitar Pinch *<br>
istortion Gtr2*<br>
ist.Rhythm Gtr*<br>
Feedback Gtr 2<br>
Gtr Feedback *<br>
Gtr Feedback<br>
ing.Slap Bass *<br>
arm Synth Bass*<br>
esonance Bass *<br>
Clavi Bass *<br>
Hammer Bass *<br>
Attack S.Bass *<br>
Rubber Bass *<br>
Attack Pulse *<br>
Resonant Bass<br>
House Bass 2<br>
Slow Violin *<br>
Slow Violin 2<br>
Yang Chin *<br>
trings & Brass*<br>
60s Strings *<br>
Orchestra<br>
ynth Strings 3*<br>
Synth Strings 3<br>
Choir Aahs 2 *<br>
Vocal Ah 2<br>
Humming *<br>
Analog Voice *<br>
Bass Hit Plus *<br>
Euro Hit *<br>
Soft Trumpet *<br>
Trombone 2 *<br>
right Trombone*<br>
ute Trumpet 2 *<br>
French Horn 2 *<br>
Octave Brass *<br>
Brass 2<br>
Synth Brass 3 *<br>
nalog Brass 1 *<br>
Jump Brass 1 *<br>
Synth Brass 3<br>
Analog Brass 1<br>
Synth Brass 4 *<br>
nalog Brass 2 *<br>
Synth Brass 4<br>
Analog Brass 2<br>
Breathy Tenor 2<br>
Bass Clarinet<br>
Square Lead 2 *<br>
Sine Lead *<br>
Sine Lead 2<br>
Saw Lead 2 *<br>
Pulse Saw *<br>
ouble Saw Lead*<br>
Sequence Saw *<br>
Saw Lead 2<br>
Wire Lead *<br>
Soft Wurl *<br>
Sine Pad *<br>
Itopia *<br>
Synth Mallet *<br>
Echo Bell *<br>
Echo Pan *<br>
Sitar 2 *<br>
Taisho Koto *<br>
Castanets *<br>
Castanets 2<br>
rch Bass Drum *<br>
rch Bass Drum 2<br>
Power Tom *<br>
Melodic Tom 2<br>
Analog Tom *<br>
Electric Drum *<br>
Synth Drum 2<br>
Cutting Noise *<br>
Thunder *<br>
Stream *<br>
Bubble *<br>
Horse Gallop *<br>
Bird Tweet 2 *<br>
Telephone 2 *<br>
Door Creaking *<br>
Scratch *<br>
Windchime *<br>
Car Engine *<br>
Car Stop *<br>
Car Pass *<br>
Car Crash *<br>
Siren *<br>
Train *<br>
Jetplane *<br>
Starship *<br>
Burst Noise *<br>
Laughing *<br>
Scream *<br>
Punch *<br>
Heart Beat *<br>
Footsteps *<br>
Machine Gun *<br>
Laser Gun *<br>
Explosion *<br>
Standard Kit*<br>
Standard Kit 1X<br>
Standard Kit 2X<br>
Room Kit *<br>
Room Kit X<br>
Power Kit *<br>
Rock Kit X<br>
Electric Kit *<br>
Electrik Kit X<br>
Analog Kit *<br>
Analog Kit X<br>
Jazz Kit *<br>
Jazz Kit X<br>
Brush Kit *<br>
Brush Kit X<br>
Orchestra Kit *<br>
Classic Kit X<br>
SFX Kit *<br>
SFX Kit 1X<br>
SFX Kit 2X<br>
Silent<br>
</div>

## Synth pad & FX voices  
<small>table @ `0x12a3c9` — 19 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Across The Void<br>
Science Fiction<br>
Vocal Frenzy<br>
Picked Ooh Pad<br>
Supersense<br>
X Brass<br>
Synthetic Lead<br>
Wild Thing<br>
Xpression Bass<br>
House Kut<br>
uzzyFilterSweep<br>
Sweppy<br>
Glimmer<br>
Dark Universe<br>
Le Cliq Bass<br>
Very Eighties<br>
Hammer Synth<br>
Fun Bass A5B5C6<br>
un Slap Bass A5<br>
</div>

## Organ / drawbar voices  
<small>table @ `0x12e0f8` — 113 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
Straight Pipes<br>
Tibia Chorus 2<br>
Tibia Chorus 3<br>
Midi Grand 3<br>
Bell Piano<br>
c.Guitar 3split<br>
Midi Guitar<br>
SynthJazzGuitar<br>
Mute Brass Ens.<br>
Clavi Lead<br>
Mallet Lead<br>
Synth Slap<br>
Windy Sweep<br>
Piano Trio<br>
Funk Staff<br>
Bonanza<br>
Multi Pitch<br>
Under Water<br>
Initial<br>
PIANO<br>
GUITAR<br>
ALLET&ORCH PERC<br>
LD      STRINGS<br>
OCAL      BRASS<br>
SAX & WOODWIND<br>
ORGAN&ACCORDION<br>
SOUND EXPLORER<br>
DIGITAL DRAWBAR<br>
ORGAN TABS<br>
ACCORD REGISTER<br>
PAD<br>
SYNTH<br>
BASS<br>
DRUM KITS<br>
MEMORY<br>
EW EXPANSION<br>
PIANO<br>
MALLET&ORCH<br>
PERC     WORLD<br>
STRINGS & VOCAL<br>
BRASS<br>
SAX & WOODWIND<br>
ORGAN&ACCORDION<br>
SOUND EXPLORER<br>
DIGITAL DRAWBAR<br>
ORGAN TABS<br>
ACCORD REGISTER<br>
PAD<br>
SYNTH<br>
BASS<br>
DRUM KITS<br>
MEMORY<br>
OUNDGROUP___063<br>
PIANO<br>
ELECTRIC PIANO<br>
HARPSI & CLAVI<br>
AC.GUITAR<br>
ELECTRIC GUITAR<br>
WORLD PERC<br>
PERCUSSION<br>
STRINGS<br>
VOCAL<br>
ELECTRIC ORGAN<br>
PIPE ORGAN<br>
ACCORDION<br>
BRASS<br>
SYNTH BRASS<br>
SAX<br>
REED<br>
FLUTE<br>
BASS<br>
S    ORCHESTRAL<br>
AD    PIANO PAD<br>
SYNTH PAD<br>
SYNTH LEAD<br>
SYNTH PERC<br>
SYNTH FX<br>
SOUND EFFECT<br>
DRUM KITS<br>
DRAWBAR & TABS<br>
GM BASIC<br>
GM2 EXTEND<br>
GM2 DRUM KITS<br>
PIANO<br>
ELECTRIC PIANO<br>
HARPSI & CLAVI<br>
MALLET<br>
& HARPELECTRIC<br>
GUITAR    WORLD<br>
PERCUSSION<br>
STRINGS<br>
VOCAL<br>
ELECTRIC ORGAN<br>
PIPE ORGAN<br>
ACCORDION<br>
BRASS<br>
SYNTH BRASS<br>
SAX<br>
REED<br>
FLUTE<br>
BASS<br>
S    ORCHESTRAL<br>
AD    PIANO PAD<br>
SYNTH PAD<br>
SYNTH LEAD<br>
SYNTH PERC<br>
SYNTH FX<br>
SOUND EFFECT<br>
DRUM KITS<br>
DRAWBAR & TABS<br>
GM BASIC<br>
GM2 EXTEND<br>
GM2 DRUM KITS<br>
</div>

## Tuning temperaments  
<small>table @ `0x1392f4` — 25 names</small>

<div style="columns:3;column-gap:1.5rem;font-size:0.85rem;">
FLAT<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
WERCKMEISTER<br>
~KIRNBERGER<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
DUMMY<br>
ARABIC 1<br>
NARABIC 2<br>
ARABIC 3<br>
NARABIC 4<br>
ARABIC 5<br>
SLENDRO<br>
PELOG<br>
PIANO<br>
ORCH<br>
</div>
