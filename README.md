Fields to be used during document creation:


|variable/payload|value|PIT_2.pdf|ZGL_CZ_RODZ_UB_ZDR.docx|REZYG_PPK.docx|OSW_PRYW_EMAIL.docx|KW_OSOB.docx|
|-|-|-|-|-|-|-|
|v|currentDate (dd-mm-yyyy)|x|x|x|x|x|
|p|employeeLastName|x|x|x|x|x|
|p|employeeFirstName|x|x|x|x|x|
|p|employeeBirthDate|x||
|p|employeePesel|x|x|x||x|
|p|employeeAddress||x|||x|
|p|employeePostalCode||x|||x|
|p|employeeCity||x|||x|
|p|employeeEmail||||x|
|p|employeePosition||||x|
|p|employerName|x|||x|
|p|employerAddress||||x|
|p|employerPostalCode||||x|
|p|employerCity||||x|
|p|employeeUserAcronym||

--------
Manual Execution:

poetry run python -m booq_document_factory.main --payload "{\"employeeLastName\":\"Kowalski\",\"employeeFirstName\":\"Jan\",\"employeeBirthDate\":\"1985-03-15\",\"employeePesel\":\"85031512345\",\"employeeAddress\":\"Ulica\",\"employeePostalCode\":\"00-001\",\"employeeCity\":\"Warsaw\",\"employeeEmail\":\"adres@email.pl\",\"employeePosition\":\"Developer\",\"employerName\":\"ABC Corporation\",\"employerAddress\":\"Employer Street 1\",\"employerPostalCode\":\"00-002\",\"employerCity\":\"Warsaw\",\"userAcronym\":\"JKowalski\"}"
--------
```bash
curl -L -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/booq-com-pl/booq-document-factory/actions/workflows/document-factory.yaml/dispatches \
  -d '{
    "ref":"main",
    "inputs": {
    "payload": "{\"employeeLastName\":\"Kowalski\",\"employeeFirstName\":\"Jan\",\"employeeBirthDate\":\"1985-03-15\",\"employeePesel\":\"85031512345\",\"employeeAddress\":\"Ulica\",\"employeePostalCode\":\"00-001\",\"employeeCity\":\"Warsaw\",\"employeeEmail\":\"adres@email.pl\",\"employeePosition\":\"Developer\",\"employerName\":\"ABC Corporation\",\"employerAddress\":\"Employer Street 1\",\"employerPostalCode\":\"00-002\",\"employerCity\":\"Warsaw\",\"userAcronym\":\"JKowalski\"}"
    }
  }'
```
-----
```json
{
    "pracImie": "Kowalski",
    "pracNazwisko": "Jan",
    "pracPesel": "85031512345",
    "pracDataUrodzenia": "1985-03-15",
    "praceNIP": "123123123",
    "pracKraj":"Polska",
    "pracWojew": "Wielkopolska",
    "pracPowiat":"xxx",
    "pracGmina":"ddd",
    "pracMiasto": "Warsaw",
    "pracUlica": "Ulica",
    "pracNrDomu": "dd",
    "pracNrLokalu":"xx",
    "pracKodPoczt": "00-001",
    "pracPoczta":"xxxx",
    "pracEmail": "adres@email.pl",
    "pracKorespKraj":"xxx",
    "pracKorespWojew":"xxx",
    "pracKorespPowiat":"xxx",
    "pracKorespGmina":"xxx",
    "pracKorespMiasto":"xxx",
    "pracKorespUlica":"xxx",
    "pracKorespNrDomu":"xxx",
    "pracKorespNrLokalu":"xxxx",
    "pracKorespKodPoczt":"xxxx",
    "pracWypadekOsoba":"xxxxx",
    "pracWypadekTelefon":"xxxxx",
    "pracWypadekAdres":"xxxx",
    "pracPaszport":"xxx",
    "pracPlec":"xxx",
    "pracKwotaZmnPod":"xxx",
    "pracSposOpodat":"xxxx",
    "pracOswKup":"xxx",
    "pracOswZwol":"xxx",
    "pracOswZwolOd":"xxx",
    "pracOswZwolDo":"xxxx",
    "pracOswOblZal":"xxx",
    "pracWnio50Proc":"xxx",
    "pracWnioNiepoZal":"xxx",
    "pracWnioNiepoZalRok":"xxxx",
    "pracNipZamPESELPit":"xxxx",
    "pracNierezyd":"xxxxx",
    "pracNierezydRodzDok":"xxxxx",
    "pracNierezydNrDok":"xxxxx",
    "pracUS":"xxxx",
    "pracDatZatr":"xxx",
    "pracDatZwol":"xxx",
    "pracDatUop":"xxx",
    "pracDatRozPra":"xxx",
    "pracRodzajUp":"xxx",
    "pracStanow": "Developer",
    "pracKodZaw":"xxxx",
    "pracGodzPra":"xxxx",
    "pracWymEtat":"xxx",
    "pracStawka":"xxx",
    "pracMieGodz":"xxx",
    "pracLimitUrloPiePra":"xxx",
    "pracOddelZagr":"xxx",
    "pracEmePrawo":"xxx",
    "pracEmeNr":"xxx",
    "pracEmeInstyt":"xxx",
    "pracRentPrawo":"xxx",
    "pracRentInstyt":"xxx",
    "pracStopieNiepel":"xxxx",
    "pracStopieNiepelZakres":"xxxxx",
    "pracDzialGosp":"xxx",
    "pracKodNFZ":"xxxx",
    "pracPPKDataRoz":"xxx",
    "pracPPKDataRez":"xxx",
    "pracBadOkrWaz":"xxx",
    "pracBankNazwa":"xxx",
    "pracIBAN":"xxx",
    "pracAkronim":"JKowalski",
    "pracodNazwa": "ABC Corporation",
    "pracodAkronim": "ABC_CORPORARTION",
    "pracodAdres": "Employer Street 1",
    "pracodKodPoczt": "00-002",
    "pracodMiasto": "Warsaw"
}
```