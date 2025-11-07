---
title: "Automatischer Export meiner Viessmann Heizung"
date: 2019-09-24
tags: viessmann data export openv cron
---

Ende 2017 haben wir die 40 Jahre alte Oelheizung durch eine neue Anlage von Viessmann ersetzt. Das moderne Geraet
stellt viele verschiedene Datenpunkte bereit und ich erklaere wie ich diese auslese und verarbeite.

![Grafana Dashboard](./heizung.png "Grafana")

## Welche Anlage besitze ich?
- [Vitoladens
  300-C](https://www.viessmann.de/de/wohngebaeude/oelheizung/oel-brennwertkessel/vitoladens-300-c.html) mit einer Vitoconnect 200
- [Vitocell](https://www.viessmann.de/de/wohngebaeude/warmwasserbereiter/heizwasser-pufferspeicher/vitocell-360-m.html)
- [5
  Solarpanele](https://www.viessmann.de/de/wohngebaeude/solarthermie/flachkollektoren/vitosol-200-fm.html)

## Welche Datenpunkte unterstuezt meine Anlage?

## Mein Influx Template
```
temperature,source=outside,provider=heating current=$1
temperature,source=warm_water,provider=heating current=$2,desired=$3,output=$4
temperature,source=reservoir,provider=heating current=$5
temperature,source=solar_collector,provider=heating current=$6
temperature,source=boiler,provider=heating current=$7,desired=$8
runtime,source=burner,provider=heating current=$9
start_count,source=burner,provider=heating current=$10
temperature,source=flow_line,provider=heating desired=$11
temperature,source=return_flow,provider=heating current=$12
status,source=pump_circulation,provider=heating current=$13
status,source=pump_heating,provider=heating current=$14
temperature,source=solar_cell,provider=heating desired=$15
runtime,source=solar,provider=heating current=$16
power,source=solar,provider=heating all_time=$17,today=$18
status,source=flame,provider=heating current=$19
status,source=pump_solar_cell,provider=heating current=$20
status,source=pump_internal,provider=heating current=$21
```
## Meine vcontrold.xml
```
xml version="1.0"?
 xmlns:vcontrol="https://www.openv.de/vcontrol">



        /dev/ttyUSB0


        3002
         ip='127.0.0.1'/>
         ip='192.168.178.0/24'/>


        /home/pi/vcontrold.log
        y
        y

       ID="20C8"/>




     name='Aktuelle Betriebsart'>
      ABA
      enum
       bytes='00' text='Abschaltbetr. (Dauernd)'/>
       bytes='01' text='Red. Betrieb (Schaltuhr)'/>
       bytes='02' text='Normalbetrieb (Schaltuhr)'/>
       bytes='03' text='Normalbetrieb (Dauernd)'/>
       text='?'/>

     name='Betriebsart'>
      BA
      enum
       bytes='00' text='Abschaltbetrieb'/>
       bytes='01' text='Nur Warmwasser'/>
       bytes='02' text='Heizen und Warmwasser'/>
       bytes='03' text='Dauernd red. Betrieb'/>
       bytes='04' text='Dauernd Normalbetrieb'/>
       text='?'/>

     name='Ferienbetrieb'>
      BFB
      uchar
       get="(B7 & (0x01<> BP"/>
       bytes='00' text='inaktiv'/>
       bytes='01' text='aktiv'/>
       text='?'/>

     name='Bitstatus'>
      BST
      uchar
       get="(B0 & (0x01<> BP"/>
       bytes='00' text='0'/>
       bytes='01' text='1'/>
       text='?'/>

     name='Anzahl'>
      CO
       get='V' set='V'/>
      int


     name='Anzahl Liter'>
      COL
       get='V/1000' set='V*1000'/>
      int
      Liter

     name='Schaltzeit'>
      CT
      cycletime

     name='Systemkennung'>
      DT
      enum
       bytes='20 CB 00 2B 00 00 01 14' text='VScotHO1, ID: 20CB, Protokoll: KW2/P300'/>
       text='?'/>

     name='Fehlermeldung'>
      EM
      errstate
       bytes='00' text='Regelbetrieb (kein Fehler)'/>
       bytes='0F' text='Wartung (für Reset Codieradresse 24 auf 0 stellen)'/>
       bytes='10' text='Kurzschluss Außentemperatursensor'/>
       bytes='18' text='Unterbrechung Außentemperatursensor'/>
       bytes='20' text='Kurzschluss Vorlauftemperatursensor'/>
       bytes='21' text='Kurzschluss Rücklauftemperatursensor'/>
       bytes='28' text='Unterbrechung Außentemperatursensor'/>
       bytes='29' text='Unterbrechung Rücklauftemperatursensor'/>
       bytes='30' text='Kurzschluss Kesseltemperatursensor'/>
       bytes='38' text='Unterbrechung Kesseltemperatursensor'/>
       bytes='40' text='Kurzschluss Vorlauftemperatursensor M2'/>
       bytes='42' text='Unterbrechung Vorlauftemperatursensor M2'/>
       bytes='50' text='Kurzschluss Speichertemperatursensor'/>
       bytes='58' text='Unterbrechung Speichertemperatursensor'/>
       bytes='92' text='Solar: Kurzschluss Kollektortemperatursensor'/>
       bytes='93' text='Solar: Kurzschluss Sensor S3'/>
       bytes='94' text='Solar: Kurzschluss Speichertemperatursensor'/>
       bytes='9A' text='Solar: Unterbrechung Kollektortemperatursensor'/>
       bytes='9B' text='Solar: Unterbrechung Sensor S3'/>
       bytes='9C' text='Solar: Unterbrechung Speichertemperatursensor'/>
       bytes='9F' text='Solar: Fehlermeldung Solarteil (siehe Solarregler)'/>
       bytes='A7' text='Bedienteil defekt'/>
       bytes='B0' text='Kurzschluss Abgastemperatursensor'/>
       bytes='B1' text='Kommunikationsfehler Bedieneinheit'/>
       bytes='B4' text='Interner Fehler (Elektronik)'/>
       bytes='B5' text='Interner Fehler (Elektronik)'/>
       bytes='B6' text='Ungültige Hardwarekennung (Elektronik)'/>
       bytes='B7' text='Interner Fehler (Kesselkodierstecker)'/>
       bytes='B8' text='Unterbrechung Abgastemperatursensor'/>
       bytes='B9' text='Interner Fehler (Dateneingabe wiederholen)'/>
       bytes='BA' text='Kommunikationsfehler Erweiterungssatz für Mischerkreis M2'/>
       bytes='BC' text='Kommunikationsfehler Fernbedienung Vitorol, Heizkreis M1'/>
       bytes='BD' text='Kommunikationsfehler Fernbedienung Vitorol, Heizkreis M2'/>
       bytes='BE' text='Falsche Codierung Fernbedienung Vitorol'/>
       bytes='C1' text='Externe Sicherheitseinrichtung (Kessel kühlt aus)'/>
       bytes='C2' text='Kommunikationsfehler Solarregelung'/>
       bytes='C5' text='Kommunikationsfehler drehzahlgeregelte Heizkreispumpe, Heizkreis M1'/>
       bytes='C6' text='Kommunikationsfehler drehzahlgeregelte Heizkreispumpe, Heizkreis M2'/>
       bytes='C7' text='Falsche Codierung der Heizkreispumpe'/>
       bytes='C9' text='Störmeldeeingang am Schaltmodul-V aktiv'/>
       bytes='CD' text='Kommunikationsfehler Vitocom 100 (KM-BUS)'/>
       bytes='CE' text='Kommunikationsfehler Schaltmodul-V'/>
       bytes='CF' text='Kommunikationsfehler LON Modul'/>
       bytes='D1' text='Brennerstörung'/>
       bytes='D4' text='Sicherheitstemperaturbegrenzer hat ausgelöst oder Störmeldemodul nicht richtig gesteckt'/>
       bytes='DA' text='Kurzschluss Raumtemperatursensor, Heizkreis M1'/>
       bytes='DB' text='Kurzschluss Raumtemperatursensor, Heizkreis M2'/>
       bytes='DD' text='Unterbrechung Raumtemperatursensor, Heizkreis M1'/>
       bytes='DE' text='Unterbrechung Raumtemperatursensor, Heizkreis M2'/>
       bytes='E4' text='Fehler Versorgungsspannung'/>
       bytes='E5' text='Interner Fehler (Ionisationselektrode)'/>
       bytes='E6' text='Abgas- / Zuluftsystem verstopft'/>
       bytes='F0' text='Interner Fehler (Regelung tauschen)'/>
       bytes='F1' text='Abgastemperaturbegrenzer ausgelöst'/>
       bytes='F2' text='Temperaturbegrenzer ausgelöst'/>
       bytes='F3' text='Flammensigal beim Brennerstart bereits vorhanden'/>
       bytes='F4' text='Flammensigal nicht vorhanden'/>
       bytes='F7' text='Differenzdrucksensor defekt'/>
       bytes='F8' text='Brennstoffventil schließt zu spät'/>
       bytes='F9' text='Gebläsedrehzahl beim Brennerstart zu niedrig'/>
       bytes='FA' text='Gebläsestillstand nicht erreicht'/>
       bytes='FD' text='Fehler Gasfeurungsautomat'/>
       bytes='FE' text='Starkes Störfeld (EMV) in der Nähe oder Elektronik defekt'/>
       bytes='FF' text='Starkes Störfeld (EMV) in der Nähe oder interner Fehler'/>
       text='?'/>

     name='Fehlerstatus'>
      ES
      enum
       bytes='00' text='kein Fehler'/>
       bytes='01' text='FEHLERMELDUNG'/>
       text='?'/>

     name='FehlermeldungGWG'>
      ESG
      enum
       bytes='00' text='Keine Störung'/>
       bytes='02' text='Fehler Sicherheitskette'/>
       bytes='04' text='Brennerstörung 04'/>
       bytes='05' text='Brennerstörung 05'/>
       bytes='07' text='Brennerstörung 07'/>
       bytes='08' text='Brennerstörung 09'/>
       bytes='08' text='Brennerstörung 09'/>
       bytes='0A' text='Brennerstörung 10'/>
       text='?'/>

     name='Flammenstatus'>
      FLS
      enum
       bytes='00' text='0'/>
       bytes='0B' text='1'/>
       text='0'/>

     name='HKP Pumpentyp'>
      HKT
      uchar
       get="(B0 & (0x01<> BP"/>
       bytes='00' text='stufig'/>
       bytes='01' text='drehzahlgeregelt'/>
       text='?'/>

     name='Laufzeit Stunden'>
      HS
       get='V/3600' set='V*3600'/>
      uint
      Stunden

     name='StatusPumpeIntern'>
      IPS
      enum
       bytes='00' text='0'/>
       bytes='01' text='1'/>
       bytes='02' text='?'/>
       bytes='03' text='0'/>
       text='?'/>

     name='Prozent'>
      PC
       get='V' set='V'/>
      uchar
      %

     name='Prozent'>
      PC1
       get='V/2' set='V*2'/>
      short
      %

     name='Prozent'>
      PC2
       get='V/10' set='V*10'/>
      uchar
      %

     name='ReturnStatus'>
      RT
      enum
       bytes='00' text='0'/>
       bytes='01' text='1'/>
       text='?'/>

     name='Sachnummer'>
      SN
      uint
       get='((((((((((((B0-48)*10)+(B1-48))*10)+(B2-48))*10)+(B3-48))*10)+(B4-48))*10)+(B5-48))*10)+B6-48'/>

     name='Quittung Status'>
      SR
      enum
       bytes='00' text='OK'/>
       bytes='05' text='SYNC (NOT OK)'/>
       text='?'/>

     name='Status'>
      ST
       get='V' set='V'/>
      char


     name='Systemzeit'>
      TI
      systime

     name='Umschaltventil Stellung'>
      USV
      enum
       bytes='00' text='UNDEFINIERT'/>
       bytes='01' text='Heizung'/>
       bytes='02' text='Mittelstellung'/>
       bytes='03' text='Warmwasser'/>
       text='?'/>

     name='Temperatur'>
      T1U
       get='V' set='V'/>
      uchar
      °C

     name='Temperatur'>
      TD
       get='V/10' set='V*10'/>
      short
      °C

     name='Temperatur'>
      T1S
       get='V/2' set='V*2'/>
      uchar
      °C

     name='Neigung'>
      UN
       get='V/10' set='V*10'/>
      short


     name='Volumenstrom'>
      VS
       get='V' set='V'/>
      ushort
      Liter



     name='P300'>
      41

         name='GETADDR'>
          SEND 00 01

         name='SETADDR'>
          SEND 00 02



         name="getaddr">
          GETADDR $addr $hexlen;RECV $len $unit

         name="setaddr">
          SETADDR $addr $hexlen;SEND BYTES $unit;RECV 1 SR



     name='KW2'>

         name='SYNC'>
          SEND 04;WAIT 05

         name='GETADDR'>
          SEND 01 F7

         name='SETADDR'>
          SEND 01 F4



         name="getaddr">
          3
          4000
          SYNC;GETADDR $addr $hexlen;RECV $len $unit

         name="setaddr">
          SYNC;SETADDR $addr $hexlen;SEND BYTES $unit;RECV 1 SR




   xmlns:xi="https://www.w3.org/2003/XInclude">
     href="vito.xml" parse="xml"/>
```
## Meine vito.xml
```
     ID="20C8" name="VDens" protocol="P300"/>




     name='getVitoBetriebsart' protocmd='getaddr'>
      2323
      1
      BA
      Betriebsart

     name='setVitoBetriebsart' protocmd='setaddr'>
      2323
      1
      BA
      Setze Betriebsart




     name='getVitoBetriebParty' protocmd='getaddr'>
      2303
      1
      RT
      Partybetrieb

     name='setVitoBetriebParty' protocmd='setaddr'>
      2303
      1
      RT
      Setze Partybetrieb

     name='getVitoTempPartySoll' protocmd='getaddr'>
      2308
      1
      T1U
      Solltemperatur Partybetrieb in °C

     name='setVitoTempPartySoll' protocmd='setaddr'>
      2308
      1
      T1U
      Setze Warmwassersolltemperatur Partybetrieb in °C




     name='getVitoBetriebFerien' protocmd='getaddr'>
      2535
      1
      BFB
      Ferienbetrieb

     name='getVitoFerienBeginn' protocmd='getaddr'>
      2309
      8
      TI
      Abreisetag

     name='setVitoFerienBeginn' protocmd='setaddr'>
      2309
      8
      TI
      Setze Abreisetag

     name='getVitoFerienEnde' protocmd='getaddr'>
      2311
      8
      TI
      Rückreisetag

     name='setVitoFerienEnde' protocmd='setaddr'>
      2311
      8
      TI
      Setze Rückreisetag




     name='getVitoBetriebSpar' protocmd='getaddr'>
      2302
      1
      RT
      Sparbetrieb

     name='setVitoBetriebSpar' protocmd='setaddr'>
      2302
      1
      RT
      Setze Sparbetrieb




     name='getVitoTempRaumNorSoll' protocmd='getaddr'>
      2306
      1
      T1U
      Raumsolltemperatur Normal in °C

     name='setVitoTempRaumNorSoll' protocmd='setaddr'>
      2306
      1
      T1U
      Setze Raumsolltemperatur Normal in °C

     name='getVitoTempRaumRedSoll' protocmd='getaddr'>
      2307
      1
      T1U
      Raumsolltemperatur reduzierter Betrieb in °C

     name='setVitoTempRaumRedSoll' protocmd='setaddr'>
      2307
      1
      T1U
      Setze Raumsolltemperatur reduzierter Betrieb in °C




     name='getVitoTempAussen' protocmd='getaddr'>
      0800
      2
      TD
      Außentemperatur in °C




     name='getVitoOelVerbrauch' protocmd='getaddr'>
      7574
      2
      COL
      Oelverbrauch




     name='getVitoTempWWIst' protocmd='getaddr'>
      0804
      2
      TD
      Warmwassertemperatur in °C

     name='getVitoTempWWSoll' protocmd='getaddr'>
      6300
      1
      T1U
      Warmwassersolltemperatur in °C

     name='setVitoTempWWSoll' protocmd='setaddr'>
      6300
      1
      T1U
      Setze Warmwassersolltemperatur in °C

     name='getVitoTempSpeicher' protocmd='getaddr'>
      0812
      2
      TD
      Speichertemperatur in °C

     name='getVitoTempWWAuslauf' protocmd='getaddr'>
      0814
      2
      TD
      Auslauftemperatur Warmwasser in °C

     name='getVitoStatusPumpeSpeicher' protocmd='getaddr'>
      6513
      1
      RT
      Status Speicherladepumpe




     name='getVitoTempKesselIst' protocmd='getaddr'>
      0810
      2
      TD
      Vorlauf- bzw. Kesseltemperatur in °C

     name='getVitoTempKesselSoll' protocmd='getaddr'>
      555A
      2
      TD
      Kesselsolltemperatur in °C

     name='getVitoStatusFlamme' protocmd='getaddr'>
      55DE
      1
      FLS
      Flammenstatus

     name='getVitoLaufzeitBrenner' protocmd='getaddr'>
      08A7
      4
      HS
      Brenner Betriebsstunden

     name='getVitoStartsBrenner' protocmd='getaddr'>
      088A
      4
      CO
      Brennerstarts

     name='getVitoStatusPumpeIntern' protocmd='getaddr'>
      7660
      1
      IPS
      Status interne Pumpe

     name='getVitoDrehzahlPumpeIntern' protocmd='getaddr'>
      7663
      1
      CO
      Drehzahl interne Pumpe




     name='getVitoKennlinieNeigung' protocmd='getaddr'>
      27D3
      1
      UN
      Neigung Heizkennlinie

     name='setVitoKennlinieNeigung' protocmd='setaddr'>
      27D3
      1
      UN
      Setze Neigung Heizkennlinie

     name='getVitoKennlinieNiveau' protocmd='getaddr'>
      27D4
      1
      ST
      Niveau Heizkennlinie

     name='setVitoKennlinieNiveau' protocmd='setaddr'>
      27D4
      1
      ST
      Setze Niveau Heizkennlinie




     name='getVitoBetriebsartHK' protocmd='getaddr'>
      2500
      1
      ABA
      Aktuelle Betriebsart des Heizkreises

     name='getVitoTempVLSoll' protocmd='getaddr'>
      2544
      2
      TD
      Vorlaufsolltemperatur in °C

     name='getVitoTempRLIst' protocmd='getaddr'>
      0808
      2
      TD
      Rücklauftemperatur in °C

     name='getVitoStatusPumpeHK' protocmd='getaddr'>
      3906
      1
      RT
      Status Heizkreispumpe

     name='getVitoTempRaumHK' protocmd='getaddr'>
      0896
      2
      TD
      Heizkreis Raumtemperatur in °C

     name='getVitoStatusPumpeZirku' protocmd='getaddr'>
      0846
      1
      RT
      Status Zirkulationspumpe




     name='getVitoTempSolarkol' protocmd='getaddr'>
      6564
      2
      TD
      Solar-Kollektortemperatur in °C

     name='getVitoTempSolarspeicher' protocmd='getaddr'>
      6566
      2
      TD
      Solar-Speichertemperatur in °C

     name='getVitoLaufzeitSolar' protocmd='getaddr'>
      6568
      2
      CO
      Solar-Betriebsstunden

     name='getVitoLeistungSolar' protocmd='getaddr'>
      6560
      4
      CO
      Solar-Wärmeenergie in kWh

     name='getVitoErtragTagSolar' protocmd='getaddr'>
      CF30
      4
      CO
      Solarertrag aktueller Tag in W




     name='getVitoStatusUmschaltventil' protocmd='getaddr'>
      0A10
      1
      USV
      Status Umschaltventil Warmwasser/Heizen




     name='getVitoTimerMoHeizen' protocmd='getaddr'>
      2000
      8
      CT
      Schaltzeit Montag

     name='setVitoTimerMoHeizen' protocmd='setaddr'>
      2000
      8
      CT
      Setze Schaltzeit Montag

     name='getVitoTimerDiHeizen' protocmd='getaddr'>
      2008
      8
      CT
      Schaltzeit Dienstag

     name='setVitoTimerDiHeizen' protocmd='setaddr'>
      2008
      8
      CT
      Setze Schaltzeit Dienstag

     name='getVitoTimerMiHeizen' protocmd='getaddr'>
      2010
      8
      CT
      Schaltzeit Mittwoch

     name='setVitoTimerMiHeizen' protocmd='setaddr'>
      2010
      8
      CT
      Setze Schaltzeit Mittwoch

     name='getVitoTimerDoHeizen' protocmd='getaddr'>
      2018
      8
      CT
      Schaltzeit Donnerstag

     name='setVitoTimerDoHeizen' protocmd='setaddr'>
      2018
      8
      CT
      Setze Schaltzeit Donnerstag

     name='getVitoTimerFrHeizen' protocmd='getaddr'>
      2020
      8
      CT
      Schaltzeit Freitag

     name='setVitoTimerFrHeizen' protocmd='setaddr'>
      2020
      8
      CT
      Setze Schaltzeit Freitag

     name='getVitoTimerSaHeizen' protocmd='getaddr'>
      2028
      8
      CT
      Schaltzeit Samstag

     name='setVitoTimerSaHeizen' protocmd='setaddr'>
      2028
      8
      CT
      Setze Schaltzeit Samstag

     name='getVitoTimerSoHeizen' protocmd='getaddr'>
      2030
      8
      CT
      Schaltzeit Sonntag

     name='setVitoTimerSoHeizen' protocmd='setaddr'>
      2030
      8
      CT
      Setze Schaltzeit Sonntag




     name='getVitoTimerMoWW' protocmd='getaddr'>
      2100
      8
      CT
      Schaltzeit Warmwasser Montag

     name='setVitoTimerMoWW' protocmd='setaddr'>
      2100
      8
      CT
      Setze Schaltzeit Warmwasser Montag

     name='getVitoTimerDiWW' protocmd='getaddr'>
      2108
      8
      CT
      Schaltzeit Warmwasser Dienstag

     name='setVitoTimerDiWW' protocmd='setaddr'>
      2108
      8
      CT
      Setze Schaltzeit Warmwasser Dienstag

     name='getVitoTimerMiWW' protocmd='getaddr'>
      2110
      8
      CT
      Schaltzeit Warmwasser Mittwoch

     name='setVitoTimerMiWW' protocmd='setaddr'>
      2110
      8
      CT
      Setze Schaltzeit Warmwasser Mittwoch

     name='getVitoTimerDoWW' protocmd='getaddr'>
      2118
      8
      CT
      Schaltzeit Warmwasser Donnerstag

     name='setVitoTimerDoWW' protocmd='setaddr'>
      2118
      8
      CT
      Setze Schaltzeit Warmwasser Donnerstag

     name='getVitoTimerFrWW' protocmd='getaddr'>
      2120
      8
      CT
      Schaltzeit Warmwasser Freitag

     name='setVitoTimerFrWW' protocmd='setaddr'>
      2120
      8
      CT
      Setze Schaltzeit Warmwasser Freitag

     name='getVitoTimerSaWW' protocmd='getaddr'>
      2128
      8
      CT
      Schaltzeit Warmwasser Samstag

     name='setVitoTimerSaWW' protocmd='setaddr'>
      2128
      8
      CT
      Setze Schaltzeit Warmwasser Samstag

     name='getVitoTimerSoWW' protocmd='getaddr'>
      2130
      8
      CT
      Schaltzeit Warmwasser Sonntag

     name='setVitoTimerSoWW' protocmd='setaddr'>
      2130
      8
      CT
      Setze Schaltzeit Warmwasser Sonntag




     name='getVitoTimerMoPumpeZirku' protocmd='getaddr'>
      2200
      8
      CT
      Schaltzeit Zirkulationspumpe Montag

     name='setVitoTimerMoPumpeZirku' protocmd='setaddr'>
      2200
      8
      CT
      Setze Schaltzeit Zirkulationspumpe Montag

     name='getVitoTimerDiPumpeZirku' protocmd='getaddr'>
      2208
      8
      CT
      Schaltzeit Zirkulationspumpe Dienstag

     name='setVitoTimerDiPumpeZirku' protocmd='setaddr'>
      2208
      8
      CT
      Setze Schaltzeit Zirkulationspumpe Dienstag

     name='getVitoTimerMiPumpeZirku' protocmd='getaddr'>
      2210
      8
      CT
      Schaltzeit Zirkulationspumpe Mittwoch

     name='setVitoTimerMiPumpeZirku' protocmd='setaddr'>
      2210
      8
      CT
      Setze Schaltzeit Zirkulationspumpe Mittwoch

     name='getVitoTimerDoPumpeZirku' protocmd='getaddr'>
      2218
      8
      CT
      Schaltzeit Zirkulationspumpe Donnerstag

     name='setVitoTimerDoPumpeZirku' protocmd='setaddr'>
      2218
      8
      CT
      Setze Schaltzeit Zirkulationspumpe Donnerstag

     name='getVitoTimerFrPumpeZirku' protocmd='getaddr'>
      2220
      8
      CT
      Schaltzeit Zirkulationspumpe Freitag

     name='setVitoTimerFrPumpeZirku' protocmd='setaddr'>
      2220
      8
      CT
      Setze Schaltzeit Zirkulationspumpe Freitag

     name='getVitoTimerSaPumpeZirku' protocmd='getaddr'>
      2228
      8
      CT
      Schaltzeit Zirkulationspumpe Samstag

     name='setVitoTimerSaPumpeZirku' protocmd='setaddr'>
      2228
      8
      CT
      Setze Schaltzeit Zirkulationspumpe Samstag

     name='getVitoTimerSoPumpeZirku' protocmd='getaddr'>
      2230
      8
      CT
      Schaltzeit Zirkulationspumpe Sonntag

     name='setVitoTimerSoPumpeZirku' protocmd='setaddr'>
      2230
      8
      CT
      Setze Schaltzeit Zirkulationspumpe Sonntag




     name='getVitoStatusStoerung' protocmd='getaddr'>
      0A82
      1
      ES
      Status Störung

     name='getVitoStoerung1' protocmd='getaddr'>
      7507
      9
      EM
      Störung Meldung 1

     name='getVitoStoerung2' protocmd='getaddr'>
      7510
      9
      EM
      Störung Meldung 2

     name='getVitoStoerung3' protocmd='getaddr'>
      7519
      9
      EM
      Störung Meldung 3

     name='getVitoStoerung4' protocmd='getaddr'>
      7522
      9
      EM
      Störung Meldung 4

     name='getVitoStoerung5' protocmd='getaddr'>
      752B
      9
      EM
      Störung Meldung 5

     name='getVitoStoerung6' protocmd='getaddr'>
      7534
      9
      EM
      Störung Meldung 6

     name='getVitoStoerung7' protocmd='getaddr'>
      753D
      9
      EM
      Störung Meldung 7

     name='getVitoStoerung8' protocmd='getaddr'>
      7546
      9
      EM
      Störung Meldung 8

     name='getVitoStoerung9' protocmd='getaddr'>
      754F
      9
      EM
      Störung Meldung 9

     name='getVitoStoerung10' protocmd='getaddr'>
      7558
      9
      EM
      Störung Meldung 10




     name='getVitoSystemzeit' protocmd='getaddr'>
      088E
      8
      TI
      Systemzeit

     name='setVitoSystemzeit' protocmd='setaddr'>
      088E
      8
      TI
      Setze Systemzeit




     name='getVitoAnlagenschema' protocmd='getaddr'>
      7700
      1
      ST
      Anlagenschema
```
