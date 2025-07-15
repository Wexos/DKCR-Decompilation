#pragma once

#include "Types.h"

class CScriptMsg;
class CStateManager;

class CEntity
{
public:
    virtual ~CEntity() = 0;

    virtual bool TypesMatch(int) const;
    virtual void PreThink(f32, CStateManager&);
    virtual void Think(f32, CStateManager&);
    virtual void AcceptScriptMsg(CStateManager&, const CScriptMsg&);
    virtual void SetActive(CStateManager&, bool);
    virtual void GetDoThinkLogic(const CStateManager&) const;
    virtual void Unk24() = 0;
};
